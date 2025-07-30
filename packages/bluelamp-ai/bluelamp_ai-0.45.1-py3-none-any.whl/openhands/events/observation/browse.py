from dataclasses import dataclass, field
from typing import Any
from openhands.core.schema import ObservationType
from openhands.events.observation.observation import Observation
@dataclass
class BrowserOutputObservation(Observation):
    """This data class represents the output of a browser."""
    url: str
    trigger_by_action: str
    screenshot: str = field(repr=False, default='')
    screenshot_path: str | None = field(default=None)
    set_of_marks: str = field(default='', repr=False)
    error: bool = False
    observation: str = ObservationType.BROWSE
    goal_image_urls: list[str] = field(default_factory=list)
    open_pages_urls: list[str] = field(default_factory=list)
    active_page_index: int = -1
    dom_object: dict[str, Any] = field(
        default_factory=dict, repr=False
    )
    axtree_object: dict[str, Any] = field(
        default_factory=dict, repr=False
    )
    extra_element_properties: dict[str, Any] = field(
        default_factory=dict, repr=False
    )
    last_browser_action: str = ''
    last_browser_action_error: str = ''
    focused_element_bid: str = ''
    @property
    def message(self) -> str:
        return 'Visited ' + self.url
    def __str__(self) -> str:
        ret = (
            '**BrowserOutputObservation**\n'
            f'URL: {self.url}\n'
            f'Error: {self.error}\n'
            f'Open pages: {self.open_pages_urls}\n'
            f'Active page index: {self.active_page_index}\n'
            f'Last browser action: {self.last_browser_action}\n'
            f'Last browser action error: {self.last_browser_action_error}\n'
            f'Focused element bid: {self.focused_element_bid}\n'
        )
        if self.screenshot_path:
            ret += f'Screenshot saved to: {self.screenshot_path}\n'
        ret += '--- Agent Observation ---\n'
        ret += self.content
        return ret