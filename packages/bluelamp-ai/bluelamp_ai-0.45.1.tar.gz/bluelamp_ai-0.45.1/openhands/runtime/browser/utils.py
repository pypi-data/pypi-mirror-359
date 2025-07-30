import base64
import datetime
import os
from pathlib import Path
from typing import Any
from browsergym.utils.obs import flatten_axtree_to_str
from PIL import Image
from openhands.core.exceptions import BrowserUnavailableException
from openhands.core.schema import ActionType
from openhands.events.action import BrowseInteractiveAction, BrowseURLAction
from openhands.events.observation import BrowserOutputObservation
from openhands.runtime.browser.base64 import png_base64_url_to_image
from openhands.runtime.browser.browser_env import BrowserEnv
from openhands.utils.async_utils import call_sync_from_async
def get_axtree_str(
    axtree_object: dict[str, Any],
    extra_element_properties: dict[str, Any],
    filter_visible_only: bool = False,
) -> str:
    cur_axtree_txt = flatten_axtree_to_str(
        axtree_object,
        extra_properties=extra_element_properties,
        with_clickable=True,
        skip_generic=False,
        filter_visible_only=filter_visible_only,
    )
    return str(cur_axtree_txt)
def get_agent_obs_text(obs: BrowserOutputObservation) -> str:
    """Get a concise text that will be shown to the agent."""
    if obs.trigger_by_action == ActionType.BROWSE_INTERACTIVE:
        text = f'[Current URL: {obs.url}]\n'
        text += f'[Focused element bid: {obs.focused_element_bid}]\n'
        if obs.screenshot_path:
            text += f'[Screenshot saved to: {obs.screenshot_path}]\n'
        text += '\n'
        if obs.error:
            text += (
                '================ BEGIN error message ===============\n'
                'The following error occurred when executing the last action:\n'
                f'{obs.last_browser_action_error}\n'
                '================ END error message ===============\n'
            )
        else:
            text += '[Action executed successfully.]\n'
        try:
            cur_axtree_txt = get_axtree_str(
                obs.axtree_object,
                obs.extra_element_properties,
                filter_visible_only=False,
            )
            text += (
                f'============== BEGIN accessibility tree ==============\n'
                f'{cur_axtree_txt}\n'
                f'============== END accessibility tree ==============\n'
            )
        except Exception as e:
            text += f'\n[Error encountered when processing the accessibility tree: {e}]'
        return text
    elif obs.trigger_by_action == ActionType.BROWSE:
        text = f'[Current URL: {obs.url}]\n'
        if obs.error:
            text += (
                '================ BEGIN error message ===============\n'
                'The following error occurred when trying to visit the URL:\n'
                f'{obs.last_browser_action_error}\n'
                '================ END error message ===============\n'
            )
        text += '============== BEGIN webpage content ==============\n'
        text += obs.content
        text += '\n============== END webpage content ==============\n'
        return text
    else:
        raise ValueError(f'Invalid trigger_by_action: {obs.trigger_by_action}')
async def browse(
    action: BrowseURLAction | BrowseInteractiveAction,
    browser: BrowserEnv | None,
    workspace_dir: str | None = None,
) -> BrowserOutputObservation:
    if browser is None:
        raise BrowserUnavailableException()
    if isinstance(action, BrowseURLAction):
        asked_url = action.url
        if not asked_url.startswith('http'):
            asked_url = os.path.abspath(os.curdir) + action.url
        action_str = f'goto("{asked_url}")'
    elif isinstance(action, BrowseInteractiveAction):
        action_str = action.browser_actions
    else:
        raise ValueError(f'Invalid action type: {action.action}')
    try:
        obs = await call_sync_from_async(browser.step, action_str)
        screenshot_path = None
        if workspace_dir is not None and obs.get('screenshot'):
            screenshots_dir = Path(workspace_dir) / '.browser_screenshots'
            screenshots_dir.mkdir(exist_ok=True)
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            screenshot_filename = f'screenshot_{timestamp}.png'
            screenshot_path = str(screenshots_dir / screenshot_filename)
            base64_data = obs.get('screenshot', '')
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            try:
                image_data = base64.b64decode(base64_data)
                with open(screenshot_path, 'wb') as f:
                    f.write(image_data)
                Image.open(screenshot_path).verify()
            except Exception:
                image = png_base64_url_to_image(obs.get('screenshot'))
                image.save(screenshot_path, format='PNG', optimize=True)
        observation = BrowserOutputObservation(
            content=obs['text_content'],
            url=obs.get('url', ''),
            screenshot=obs.get('screenshot', None),
            screenshot_path=screenshot_path,
            set_of_marks=obs.get(
                'set_of_marks', None
            ),
            goal_image_urls=obs.get('image_content', []),
            open_pages_urls=obs.get('open_pages_urls', []),
            active_page_index=obs.get(
                'active_page_index', -1
            ),
            axtree_object=obs.get('axtree_object', {}),
            extra_element_properties=obs.get('extra_element_properties', {}),
            focused_element_bid=obs.get(
                'focused_element_bid', None
            ),
            last_browser_action=obs.get(
                'last_action', ''
            ),
            last_browser_action_error=obs.get('last_action_error', ''),
            error=True if obs.get('last_action_error', '') else False,
            trigger_by_action=action.action,
        )
        observation.content = get_agent_obs_text(observation)
        if not action.return_axtree:
            observation.dom_object = {}
            observation.axtree_object = {}
            observation.extra_element_properties = {}
        return observation
    except Exception as e:
        error_message = str(e)
        error_url = asked_url if action.action == ActionType.BROWSE else ''
        observation = BrowserOutputObservation(
            content=error_message,
            screenshot='',
            screenshot_path=None,
            error=True,
            last_browser_action_error=error_message,
            url=error_url,
            trigger_by_action=action.action,
        )
        try:
            observation.content = get_agent_obs_text(observation)
        except Exception:
            pass
        return observation