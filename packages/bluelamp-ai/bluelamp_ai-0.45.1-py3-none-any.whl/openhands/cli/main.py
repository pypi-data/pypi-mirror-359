import asyncio
import logging
import os
import signal
import sys
import threading
import time
if os.environ.get('TERM') in ['dumb', 'unknown'] or not sys.stdout.isatty():
    os.environ['PROMPT_TOOLKIT_NO_CPR'] = '1'
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import clear
import openhands.agenthub
import openhands.cli.suppress_warnings
from openhands.cli.commands import (
    check_folder_security_agreement,
    handle_commands,
)
from openhands.cli.settings import modify_llm_settings_basic
from openhands.cli.branding import get_message
from openhands.cli.tui import (
    UsageMetrics,
    display_agent_running_message,
    display_banner,
    display_event,
    display_initial_user_prompt,
    display_initialization_animation,
    display_runtime_initialization_message,
    display_welcome_message,
    process_agent_pause,
    read_confirmation_input,
    read_prompt_input,
    update_streaming_output,
)
from openhands.cli.utils import (
    update_usage_metrics,
)
from openhands.controller import AgentController
from openhands.controller.agent import Agent
from openhands.core.config import (
    OpenHandsConfig,
    parse_arguments,
    setup_config_from_args,
)
from openhands.core.config.condenser_config import NoOpCondenserConfig
from openhands.core.config.mcp_config import OpenHandsMCPConfigImpl
from openhands.core.logger import bluelamp_logger as logger
from openhands.core.loop import run_agent_until_done
from openhands.core.schema import AgentState
from openhands.core.setup import (
    create_agent,
    create_controller,
    create_memory,
    create_runtime,
    generate_sid,
    initialize_repository_for_runtime,
)
from openhands.events import EventSource, EventStreamSubscriber
from openhands.events.action import (
    ChangeAgentStateAction,
    MessageAction,
)
from openhands.events.event import Event
from openhands.events.observation import (
    AgentStateChangedObservation,
)
from openhands.io import read_task
from openhands.mcp import add_mcp_tools_to_agent
from openhands.memory.condenser.impl.llm_summarizing_condenser import (
    LLMSummarizingCondenserConfig,
)
from openhands.microagent.microagent import BaseMicroagent
from openhands.runtime.base import Runtime
from openhands.storage.settings.file_settings_store import FileSettingsStore
_shutdown_requested = threading.Event()
_shutdown_lock = threading.Lock()
def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        print_formatted_text(HTML(f'\n<blue>{get_message("ctrl_c_exit")}</blue>'))
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
async def cleanup_session(
    loop: asyncio.AbstractEventLoop,
    agent: Agent,
    runtime: Runtime,
    controller: AgentController,
) -> None:
    """Clean up all resources from the current session."""
    logger.info("CTRL+C_DEBUG: Starting session cleanup...")
    try:
        event_stream = runtime.event_stream
        end_state = controller.get_state()
        end_state.save_to_session(
            event_stream.sid,
            event_stream.file_store,
            event_stream.user_id,
        )
        logger.info("CTRL+C_DEBUG: Session state saved")
    except Exception as e:
        logger.warning(f"CTRL+C_DEBUG: Failed to save session state: {e}")
    try:
        current_task = asyncio.current_task(loop)
        pending = [task for task in asyncio.all_tasks(loop) if task is not current_task]
        logger.info(f"CTRL+C_DEBUG: Found {len(pending)} pending tasks to cancel")
        if pending:
            for task in pending:
                if not task.done():
                    task.cancel()
                    logger.debug(f"CTRL+C_DEBUG: Cancelled task: {task.get_name()}")
            try:
                done, pending_set = await asyncio.wait(set(pending), timeout=5.0)
                remaining_pending = list(pending_set)
                logger.info(f"CTRL+C_DEBUG: {len(done)} tasks completed, {len(remaining_pending)} still pending")
                for task in remaining_pending:
                    if not task.done():
                        task.cancel()
                        logger.warning(f"CTRL+C_DEBUG: Force cancelled task: {task.get_name()}")
            except asyncio.TimeoutError:
                logger.warning("CTRL+C_DEBUG: Timeout waiting for tasks to complete")
        logger.info("CTRL+C_DEBUG: Cleaning up agent and runtime...")
        agent.reset()
        runtime.close()
        await controller.close()
        logger.info("CTRL+C_DEBUG: Session cleanup completed successfully")
    except Exception as e:
        logger.error(f'CTRL+C_DEBUG: Error during session cleanup: {e}')
        import traceback
        logger.error(f'CTRL+C_DEBUG: Cleanup traceback: {traceback.format_exc()}')
async def background_auth_check(config: OpenHandsConfig, check_interval: int = 600) -> None:
    """Background task to periodically check authentication status.
    Args:
        config: Application configuration
        check_interval: Check interval in seconds (default 600 = 10 minutes)
    """
    from openhands.cli.auth import get_authenticator
    portal_url = config.portal_base_url or "https://bluelamp-235426778039.asia-northeast1.run.app/api"
    authenticator = get_authenticator(portal_url)
    while not _shutdown_requested.is_set():
        try:
            await asyncio.sleep(check_interval)
            if _shutdown_requested.is_set():
                break
            try:
                await authenticator.verify_api_key()
                logger.debug("Background auth check: Still authenticated")
            except ValueError as e:
                logger.warning(f"Background auth check failed: {e}")
                print_formatted_text(
                    HTML(f'\n<red>{get_message("portal_auth_check_failed")}</red>')
                )
                _shutdown_requested.set()
                break
            except Exception as e:
                if "Authentication service unavailable" in str(e):
                    logger.error(f"Background auth check failed: {e}")
                    print_formatted_text(
                        HTML(f'\n<red>認証サービスに接続できません。CLIを終了します。</red>')
                    )
                    _shutdown_requested.set()
                    break
                else:
                    logger.debug(f"Background auth check network error: {e}")
        except asyncio.CancelledError:
            logger.debug("Background auth check cancelled")
            break
async def run_session(
    loop: asyncio.AbstractEventLoop,
    config: OpenHandsConfig,
    settings_store: FileSettingsStore,
    current_dir: str,
    task_content: str | None = None,
    conversation_instructions: str | None = None,
    session_name: str | None = None,
    skip_banner: bool = False,
) -> bool:
    reload_microagents = False
    new_session_requested = False
    sid = generate_sid(config, session_name)
    is_loaded = asyncio.Event()
    is_paused = asyncio.Event()
    always_confirm_mode = False
    display_runtime_initialization_message(config.runtime)
    loop.run_in_executor(
        None, display_initialization_animation, 'Initializing...', is_loaded
    )
    agent = create_agent(config)
    runtime = create_runtime(
        config,
        sid=sid,
        headless_mode=True,
        agent=agent,
    )
    def stream_to_console(output: str) -> None:
        update_streaming_output(output)
    runtime.subscribe_to_shell_stream(stream_to_console)
    controller, initial_state = create_controller(agent, runtime, config, headless_mode=True)
    event_stream = runtime.event_stream
    usage_metrics = UsageMetrics()
    auth_check_task = None
    portal_url = config.portal_base_url or "https://bluelamp-235426778039.asia-northeast1.run.app/api"
    config.portal_base_url = portal_url
    auth_check_task = asyncio.create_task(background_auth_check(config))
    logger.debug("Started background authentication check task")
    async def prompt_for_next_task(agent_state: str) -> None:
        nonlocal reload_microagents, new_session_requested
        while True:
            if _shutdown_requested.is_set():
                logger.info("CTRL+C_DEBUG: Shutdown requested, exiting prompt loop")
                return
            next_message = await read_prompt_input(
                agent_state, multiline=config.cli_multiline_input
            )
            if _shutdown_requested.is_set():
                logger.info("CTRL+C_DEBUG: Shutdown requested after input, exiting prompt loop")
                return
            if not next_message.strip():
                continue
            (
                close_repl,
                reload_microagents,
                new_session_requested,
            ) = await handle_commands(
                next_message,
                event_stream,
                usage_metrics,
                sid,
                config,
                current_dir,
                settings_store,
            )
            if close_repl or _shutdown_requested.is_set():
                return
    async def on_event_async(event: Event) -> None:
        nonlocal reload_microagents, is_paused, always_confirm_mode
        if _shutdown_requested.is_set():
            logger.info("CTRL+C_DEBUG: Shutdown requested, skipping event processing")
            return
        logging.info(f"AGENT_SWITCH_DEBUG: Processing event: {type(event).__name__}")
        if isinstance(event, AgentStateChangedObservation):
            logging.info(f"AGENT_SWITCH_DEBUG: AgentStateChangedObservation - state: {event.agent_state}")
        display_event(event, config)
        update_usage_metrics(event, usage_metrics)
        if isinstance(event, AgentStateChangedObservation):
            if event.agent_state in [
                AgentState.AWAITING_USER_INPUT,
                AgentState.FINISHED,
            ]:
                if is_paused.is_set():
                    return
                if reload_microagents:
                    microagents: list[BaseMicroagent] = (
                        runtime.get_microagents_from_selected_repo(None)
                    )
                    memory.load_user_workspace_microagents(microagents)
                    reload_microagents = False
                await prompt_for_next_task(event.agent_state)
            if event.agent_state == AgentState.PAUSED:
                is_paused.clear()
                await prompt_for_next_task(event.agent_state)
            if event.agent_state == AgentState.RUNNING:
                display_agent_running_message()
                loop.create_task(
                    process_agent_pause(is_paused, event_stream)
                )
    def on_event(event: Event) -> None:
        loop.create_task(on_event_async(event))
    event_stream.subscribe(EventStreamSubscriber.MAIN, on_event, sid)
    await runtime.connect()
    repo_directory = None
    if config.sandbox.selected_repo:
        repo_directory = initialize_repository_for_runtime(
            runtime,
            selected_repository=config.sandbox.selected_repo,
        )
    memory = create_memory(
        runtime=runtime,
        event_stream=event_stream,
        sid=sid,
        selected_repository=config.sandbox.selected_repo,
        repo_directory=repo_directory,
        conversation_instructions=conversation_instructions,
    )
    if agent.config.enable_mcp:
        _, openhands_mcp_stdio_servers = (
            OpenHandsMCPConfigImpl.create_default_mcp_server_config(
                config.mcp_host, config, None
            )
        )
        runtime.config.mcp.stdio_servers.extend(openhands_mcp_stdio_servers)
        await add_mcp_tools_to_agent(agent, runtime, memory)
    is_loaded.set()
    clear()
    if not skip_banner:
        display_banner(session_id=sid)
    welcome_message = get_message('build_prompt')
    initial_message = ''
    if task_content:
        initial_message = task_content
    if initial_state is not None:
        logger.info(f'Resuming session: {sid}')
        print_formatted_text(HTML(f'<grey>{get_message("session_resumed", sid=sid)}</grey>'))
        if initial_state.last_error:
            initial_message = get_message('session_error_recovery')
        else:
            initial_message = ''
            welcome_message += f'\n{get_message("loading_previous")}'
    display_welcome_message(welcome_message)
    if initial_message:
        display_initial_user_prompt(initial_message)
        event_stream.add_event(MessageAction(content=initial_message), EventSource.USER)
    else:
        asyncio.create_task(prompt_for_next_task(''))
    await run_agent_until_done(
        controller, runtime, memory, [AgentState.STOPPED, AgentState.ERROR, AgentState.FINISHED]
    )
    if auth_check_task and not auth_check_task.done():
        auth_check_task.cancel()
        try:
            await auth_check_task
        except asyncio.CancelledError:
            logger.debug("Background auth check task cancelled")
    await cleanup_session(loop, agent, runtime, controller)
    return new_session_requested
async def run_setup_flow(config: OpenHandsConfig, settings_store: FileSettingsStore):
    """Run the setup flow to configure initial settings.
    Returns:
        bool: True if settings were successfully configured, False otherwise.
    """
    display_banner(session_id='setup')
    print_formatted_text(
        HTML(f'<grey>{get_message("no_settings")}</grey>\n')
    )
    await modify_llm_settings_basic(config, settings_store)
async def main_with_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Runs the agent in CLI mode."""
    args = parse_arguments()
    logger.setLevel(logging.WARNING)
    config: OpenHandsConfig = setup_config_from_args(args)
    from openhands.security.system_init import initialize_system_components
    initialize_system_components()
    settings_store = await FileSettingsStore.get_instance(config=config, user_id=None)
    settings = await settings_store.load()
    banner_shown = False
    if not settings:
        clear()
        await run_setup_flow(config, settings_store)
        banner_shown = True
        settings = await settings_store.load()
    from openhands.cli.auth import get_authenticator
    portal_url = config.portal_base_url or "https://bluelamp-235426778039.asia-northeast1.run.app/api"
    authenticator = get_authenticator(portal_url)
    saved_api_key = authenticator.load_api_key()
    if not saved_api_key:
        clear()
        if not banner_shown:
            display_banner(session_id='auth')
            banner_shown = True
        print_formatted_text(
            HTML(f'<yellow>{get_message("portal_auth_required")}</yellow>\n')
        )
        print_formatted_text(
            HTML(f'<grey>{get_message("portal_auth_prompt")}</grey>\n')
        )
        try:
            success = await authenticator.prompt_for_login()
            if not success:
                print_formatted_text(HTML(f'<red>{get_message("portal_auth_cancelled")}</red>'))
                return
        except Exception as e:
            print_formatted_text(HTML(f'<red>{get_message("portal_network_error", error=str(e))}</red>\n'))
            print_formatted_text(HTML(f'<grey>{get_message("portal_connection_check")}</grey>\n'))
            return
    else:
        try:
            await authenticator.verify_api_key()
            user_info = authenticator.get_user_info()
            if not banner_shown:
                clear()
                display_banner(session_id='authenticated')
                banner_shown = True
            print_formatted_text(
                HTML(f'<green>{get_message("portal_authenticated", name=user_info.get("name"))}</green>\n')
            )
        except ValueError as e:
            print_formatted_text(HTML(f'<red>{get_message("portal_auth_error", error=str(e))}</red>'))
            print_formatted_text(HTML(f'<yellow>{get_message("portal_key_invalid")}</yellow>\n'))
            authenticator.clear_auth()
            try:
                success = await authenticator.prompt_for_login()
                if not success:
                    print_formatted_text(HTML(f'<red>{get_message("portal_auth_cancelled")}</red>'))
                    return
                user_info = authenticator.get_user_info()
                print_formatted_text(
                    HTML(f'<green>認証成功: {user_info.get("name")} としてログインしました。</green>\n')
                )
            except ValueError as e:
                print_formatted_text(HTML(f'<red>{get_message("portal_auth_error", error=str(e))}</red>\n'))
                return
            except Exception as e:
                print_formatted_text(HTML(f'<red>{get_message("portal_network_error", error=str(e))}</red>\n'))
                return
        except Exception as e:
            if "Authentication service unavailable" in str(e):
                print_formatted_text(
                    HTML(f'<red>認証サービスに接続できません。CLIを終了します。</red>')
                )
                return
            else:
                print_formatted_text(
                    HTML(f'<yellow>{get_message("portal_connection_error", error=str(e))}</yellow>')
                )
                print_formatted_text(
                    HTML(f'<yellow>{get_message("portal_offline_mode")}</yellow>\n')
                )
    if settings:
        if args.agent_cls:
            config.default_agent = str(args.agent_cls)
        else:
            assert settings.agent is not None
            config.default_agent = settings.agent
        if not args.llm_config and settings.llm_model and settings.llm_api_key:
            llm_config = config.get_llm_config()
            llm_config.model = settings.llm_model
            llm_config.api_key = settings.llm_api_key
            llm_config.base_url = settings.llm_base_url
            config.set_llm_config(llm_config)
        config.security.confirmation_mode = (
            settings.confirmation_mode if settings.confirmation_mode else False
        )
        if settings.enable_default_condenser:
            llm_config = config.get_llm_config()
            agent_config = config.get_agent_config(config.default_agent)
            agent_config.condenser = LLMSummarizingCondenserConfig(
                llm_config=llm_config,
                type='llm',
            )
            config.set_agent_config(agent_config)
            config.enable_default_condenser = True
        else:
            agent_config = config.get_agent_config(config.default_agent)
            agent_config.condenser = NoOpCondenserConfig(type='noop')
            config.set_agent_config(agent_config)
            config.enable_default_condenser = False
    val_override = args.override_cli_mode
    should_override_cli_defaults = (
        val_override is True
        or (isinstance(val_override, str) and val_override.lower() in ('true', '1'))
        or (isinstance(val_override, int) and val_override == 1)
    )
    if not should_override_cli_defaults:
        config.runtime = 'cli'
        config.security.confirmation_mode = True
    current_dir = os.getcwd()
    if not current_dir:
        raise ValueError('Workspace base directory not specified')
    if not check_folder_security_agreement(config, current_dir):
        return
    task_str = read_task(args, config.cli_multiline_input)
    new_session_requested = await run_session(
        loop,
        config,
        settings_store,
        current_dir,
        task_str,
        session_name=args.name,
        skip_banner=banner_shown,
    )
    while new_session_requested and not _shutdown_requested.is_set():
        new_session_requested = await run_session(
            loop, config, settings_store, current_dir, None
        )
def main():
    setup_signal_handlers()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    logger.setLevel(logging.INFO)
    logger.info("CTRL+C_DEBUG: Starting BlueLamp CLI application")
    try:
        loop.run_until_complete(main_with_loop(loop))
        logger.info("CTRL+C_DEBUG: Main loop completed normally")
    except KeyboardInterrupt:
        logger.info("CTRL+C_DEBUG: KeyboardInterrupt caught in main()")
        print_formatted_text(HTML('<gold>Received keyboard interrupt, shutting down...</gold>'))
        _shutdown_requested.set()
    except ConnectionRefusedError as e:
        print(get_message('error_connection', error=str(e)))
        sys.exit(1)
    except Exception as e:
        import traceback
        print(get_message('error_generic', error=str(e)))
        traceback.print_exc()
        sys.exit(1)
    finally:
        logger.info("CTRL+C_DEBUG: Starting final cleanup...")
        try:
            pending = asyncio.all_tasks(loop)
            logger.info(f"CTRL+C_DEBUG: Cancelling {len(pending)} pending tasks")
            for task in pending:
                if not task.done():
                    task.cancel()
                    logger.debug(f"CTRL+C_DEBUG: Cancelled task in main: {task.get_name()}")
            if pending:
                try:
                    loop.run_until_complete(
                        asyncio.wait_for(
                            asyncio.gather(*pending, return_exceptions=True),
                            timeout=3.0
                        )
                    )
                    logger.info("CTRL+C_DEBUG: All tasks completed successfully")
                except asyncio.TimeoutError:
                    logger.warning("CTRL+C_DEBUG: Timeout waiting for tasks in main cleanup")
                except Exception as cleanup_error:
                    logger.warning(f"CTRL+C_DEBUG: Error during task cleanup: {cleanup_error}")
            loop.close()
            logger.info("CTRL+C_DEBUG: Event loop closed")
        except Exception as e:
            logger.error(f'CTRL+C_DEBUG: Error during final cleanup: {e}')
            print(f'Error during cleanup: {e}')
            sys.exit(1)
        logger.info("CTRL+C_DEBUG: Application shutdown complete")
if __name__ == '__main__':
    main()