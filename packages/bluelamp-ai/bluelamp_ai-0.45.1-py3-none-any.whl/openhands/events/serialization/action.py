from typing import Any
from openhands.core.exceptions import LLMMalformedActionError
from openhands.events.action.action import Action
from openhands.events.action.agent import (
    AgentDelegateAction,
    AgentFinishAction,
    AgentRejectAction,
    AgentThinkAction,
    ChangeAgentStateAction,
    CondensationAction,
    RecallAction,
)
from openhands.events.action.browse import BrowseInteractiveAction, BrowseURLAction
from openhands.events.action.commands import (
    CmdRunAction,
    IPythonRunCellAction,
)
from openhands.events.action.empty import NullAction
from openhands.events.action.files import (
    FileEditAction,
    FileReadAction,
    FileWriteAction,
)
from openhands.events.action.mcp import MCPAction
from openhands.events.action.message import MessageAction, SystemMessageAction
actions = (
    NullAction,
    CmdRunAction,
    IPythonRunCellAction,
    BrowseURLAction,
    BrowseInteractiveAction,
    FileReadAction,
    FileWriteAction,
    FileEditAction,
    AgentThinkAction,
    AgentFinishAction,
    AgentRejectAction,
    AgentDelegateAction,
    RecallAction,
    ChangeAgentStateAction,
    MessageAction,
    SystemMessageAction,
    CondensationAction,
    MCPAction,
)
ACTION_TYPE_TO_CLASS = {action_class.action: action_class for action_class in actions}
def handle_action_deprecated_args(args: dict[str, Any]) -> dict[str, Any]:
    if 'keep_prompt' in args:
        args.pop('keep_prompt')
    if 'translated_ipython_code' in args:
        code = args.pop('translated_ipython_code')
        file_editor_prefix = 'print(file_editor(**'
        if (
            code is not None
            and code.startswith(file_editor_prefix)
            and code.endswith('))')
        ):
            try:
                import ast
                dict_str = code[len(file_editor_prefix) : -2]
                file_args = ast.literal_eval(dict_str)
                args.update(file_args)
            except (ValueError, SyntaxError):
                pass
        if args.get('command') == 'view':
            args.pop(
                'command'
            )
    return args
def action_from_dict(action: dict) -> Action:
    if not isinstance(action, dict):
        raise LLMMalformedActionError('action must be a dictionary')
    action = action.copy()
    if 'action' not in action:
        raise LLMMalformedActionError(f"'action' key is not found in {action=}")
    if not isinstance(action['action'], str):
        raise LLMMalformedActionError(
            f"'{action['action']=}' is not defined. Available actions: {ACTION_TYPE_TO_CLASS.keys()}"
        )
    action_class = ACTION_TYPE_TO_CLASS.get(action['action'])
    if action_class is None:
        raise LLMMalformedActionError(
            f"'{action['action']=}' is not defined. Available actions: {ACTION_TYPE_TO_CLASS.keys()}"
        )
    args = action.get('args', {})
    timestamp = args.pop('timestamp', None)
    is_confirmed = args.pop('is_confirmed', None)
    if is_confirmed is not None:
        args['confirmation_state'] = is_confirmed
    if 'images_urls' in args:
        args['image_urls'] = args.pop('images_urls')
    args = handle_action_deprecated_args(args)
    try:
        decoded_action = action_class(**args)
        if 'timeout' in action:
            blocking = args.get('blocking', False)
            decoded_action.set_hard_timeout(action['timeout'], blocking=blocking)
        if timestamp:
            decoded_action._timestamp = timestamp
    except TypeError as e:
        raise LLMMalformedActionError(
            f'action={action} has the wrong arguments: {str(e)}'
        )
    assert isinstance(decoded_action, Action)
    return decoded_action