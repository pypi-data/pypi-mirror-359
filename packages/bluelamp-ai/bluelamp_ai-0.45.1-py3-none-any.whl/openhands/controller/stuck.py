from openhands.controller.state.state import State
from openhands.core.logger import openhands_logger as logger
from openhands.events.action.action import Action
from openhands.events.action.commands import IPythonRunCellAction
from openhands.events.action.empty import NullAction
from openhands.events.action.message import MessageAction
from openhands.events.event import Event, EventSource
from openhands.events.observation import (
    CmdOutputObservation,
    IPythonRunCellObservation,
)
from openhands.events.observation.agent import AgentCondensationObservation
from openhands.events.observation.empty import NullObservation
from openhands.events.observation.error import ErrorObservation
from openhands.events.observation.observation import Observation
class StuckDetector:
    SYNTAX_ERROR_MESSAGES = [
        'SyntaxError: unterminated string literal (detected at line',
        'SyntaxError: invalid syntax. Perhaps you forgot a comma?',
        'SyntaxError: incomplete input',
    ]
    def __init__(self, state: State):
        self.state = state
    def is_stuck(self, headless_mode: bool = True) -> bool:
        """Checks if the agent is stuck in a loop.
        Args:
            headless_mode: Matches AgentController's headless_mode.
                          If True: Consider all history (automated/testing)
                          If False: Consider only history after last user message (interactive)
        Returns:
            bool: True if the agent is stuck in a loop, False otherwise.
        """
        if not headless_mode:
            last_user_msg_idx = -1
            for i, event in enumerate(reversed(self.state.history)):
                if (
                    isinstance(event, MessageAction)
                    and event.source == EventSource.USER
                ):
                    last_user_msg_idx = len(self.state.history) - i - 1
                    break
            history_to_check = self.state.history[last_user_msg_idx + 1 :]
        else:
            history_to_check = self.state.history
        filtered_history = [
            event
            for event in history_to_check
            if not (
                (isinstance(event, MessageAction) and event.source == EventSource.USER)
                or isinstance(event, (NullAction, NullObservation))
            )
        ]
        if len(filtered_history) < 3:
            return False
        last_actions: list[Event] = []
        last_observations: list[Event] = []
        for event in reversed(filtered_history):
            if isinstance(event, Action) and len(last_actions) < 4:
                last_actions.append(event)
            elif isinstance(event, Observation) and len(last_observations) < 4:
                last_observations.append(event)
            if len(last_actions) == 4 and len(last_observations) == 4:
                break
        if self._is_stuck_repeating_action_observation(last_actions, last_observations):
            return True
        if self._is_stuck_repeating_action_error(last_actions, last_observations):
            return True
        if self._is_stuck_monologue(filtered_history):
            return True
        if len(filtered_history) >= 6:
            if self._is_stuck_action_observation_pattern(filtered_history):
                return True
        if len(filtered_history) >= 10:
            if self._is_stuck_context_window_error(filtered_history):
                return True
        return False
    def _is_stuck_repeating_action_observation(
        self, last_actions: list[Event], last_observations: list[Event]
    ) -> bool:
        if len(last_actions) == 4 and len(last_observations) == 4:
            actions_equal = all(
                self._eq_no_pid(last_actions[0], action) for action in last_actions
            )
            observations_equal = all(
                self._eq_no_pid(last_observations[0], observation)
                for observation in last_observations
            )
            if actions_equal and observations_equal:
                logger.warning('Action, Observation loop detected')
                return True
        return False
    def _is_stuck_repeating_action_error(
        self, last_actions: list[Event], last_observations: list[Event]
    ) -> bool:
        if len(last_actions) < 3 or len(last_observations) < 3:
            return False
        if all(self._eq_no_pid(last_actions[0], action) for action in last_actions[:3]):
            if all(isinstance(obs, ErrorObservation) for obs in last_observations[:3]):
                logger.warning('Action, ErrorObservation loop detected')
                return True
            elif all(
                isinstance(obs, IPythonRunCellObservation)
                for obs in last_observations[:3]
            ):
                warning = 'Action, IPythonRunCellObservation loop detected'
                for error_message in self.SYNTAX_ERROR_MESSAGES:
                    if error_message.startswith(
                        'SyntaxError: unterminated string literal (detected at line'
                    ):
                        if self._check_for_consistent_line_error(
                            [
                                obs
                                for obs in last_observations[:3]
                                if isinstance(obs, IPythonRunCellObservation)
                            ],
                            error_message,
                        ):
                            logger.warning(warning)
                            return True
                    elif error_message in (
                        'SyntaxError: invalid syntax. Perhaps you forgot a comma?',
                        'SyntaxError: incomplete input',
                    ) and self._check_for_consistent_invalid_syntax(
                        [
                            obs
                            for obs in last_observations[:3]
                            if isinstance(obs, IPythonRunCellObservation)
                        ],
                        error_message,
                    ):
                        logger.warning(warning)
                        return True
        return False
    def _check_for_consistent_invalid_syntax(
        self, observations: list[IPythonRunCellObservation], error_message: str
    ) -> bool:
        first_lines = []
        valid_observations = []
        for obs in observations:
            content = obs.content
            lines = content.strip().split('\n')
            if len(lines) < 6:
                return False
            line1 = lines[0].strip()
            if not line1.startswith('Cell In[1], line'):
                return False
            first_lines.append(line1)
            if (
                lines[-1].startswith('[Jupyter Python interpreter:')
                and lines[-2].startswith('[Jupyter current working directory:')
                and error_message in lines[-3]
            ):
                valid_observations.append(obs)
        return (
            len(set(first_lines)) == 1
            and len(valid_observations) == 3
            and len(
                set(
                    obs.content.strip().split('\n')[:-2][-1]
                    for obs in valid_observations
                )
            )
            == 1
        )
    def _check_for_consistent_line_error(
        self, observations: list[IPythonRunCellObservation], error_message: str
    ) -> bool:
        error_lines = []
        for obs in observations:
            content = obs.content
            lines = content.strip().split('\n')
            if len(lines) < 3:
                return False
            last_lines = lines[-3:]
            if not (
                last_lines[-2].startswith('[Jupyter current working directory:')
                and last_lines[-1].startswith('[Jupyter Python interpreter:')
            ):
                return False
            if error_message in last_lines[-3]:
                error_lines.append(last_lines[-3])
        return len(error_lines) == 3 and len(set(error_lines)) == 1
    def _is_stuck_monologue(self, filtered_history: list[Event]) -> bool:
        agent_message_actions = [
            (i, event)
            for i, event in enumerate(filtered_history)
            if isinstance(event, MessageAction) and event.source == EventSource.AGENT
        ]
        if len(agent_message_actions) >= 3:
            last_agent_message_actions = agent_message_actions[-3:]
            if all(
                (last_agent_message_actions[0][1] == action[1])
                for action in last_agent_message_actions
            ):
                start_index = last_agent_message_actions[0][0]
                end_index = last_agent_message_actions[-1][0]
                has_observation_between = False
                for event in filtered_history[start_index + 1 : end_index]:
                    if isinstance(event, Observation):
                        has_observation_between = True
                        break
                if not has_observation_between:
                    logger.warning('Repeated MessageAction with source=AGENT detected')
                    return True
        return False
    def _is_stuck_action_observation_pattern(
        self, filtered_history: list[Event]
    ) -> bool:
        last_six_actions: list[Event] = []
        last_six_observations: list[Event] = []
        for event in reversed(filtered_history):
            if isinstance(event, Action) and len(last_six_actions) < 6:
                last_six_actions.append(event)
            elif isinstance(event, Observation) and len(last_six_observations) < 6:
                last_six_observations.append(event)
            if len(last_six_actions) == 6 and len(last_six_observations) == 6:
                break
        if len(last_six_actions) == 6 and len(last_six_observations) == 6:
            actions_equal = (
                self._eq_no_pid(last_six_actions[0], last_six_actions[2])
                and self._eq_no_pid(last_six_actions[0], last_six_actions[4])
                and self._eq_no_pid(last_six_actions[1], last_six_actions[3])
                and self._eq_no_pid(last_six_actions[1], last_six_actions[5])
            )
            observations_equal = (
                self._eq_no_pid(last_six_observations[0], last_six_observations[2])
                and self._eq_no_pid(last_six_observations[0], last_six_observations[4])
                and self._eq_no_pid(last_six_observations[1], last_six_observations[3])
                and self._eq_no_pid(last_six_observations[1], last_six_observations[5])
            )
            if actions_equal and observations_equal:
                logger.warning('Action, Observation pattern detected')
                return True
        return False
    def _is_stuck_context_window_error(self, filtered_history: list[Event]) -> bool:
        """Detects if we're stuck in a loop of context window errors.
        This happens when we repeatedly get context window errors and try to trim,
        but the trimming doesn't work, causing us to get more context window errors.
        The pattern is repeated AgentCondensationObservation events without any other
        events between them.
        Args:
            filtered_history: List of filtered events to check
        Returns:
            bool: True if we detect a context window error loop
        """
        condensation_events = [
            (i, event)
            for i, event in enumerate(filtered_history)
            if isinstance(event, AgentCondensationObservation)
        ]
        if len(condensation_events) < 10:
            return False
        last_condensation_events = condensation_events[-10:]
        for i in range(len(last_condensation_events) - 1):
            start_idx = last_condensation_events[i][0]
            end_idx = last_condensation_events[i + 1][0]
            has_other_events = False
            for event in filtered_history[start_idx + 1 : end_idx]:
                if not isinstance(event, AgentCondensationObservation):
                    has_other_events = True
                    break
            if not has_other_events:
                logger.warning(
                    'Context window error loop detected - repeated condensation events'
                )
                return True
        return False
    def _eq_no_pid(self, obj1: Event, obj2: Event) -> bool:
        if isinstance(obj1, IPythonRunCellAction) and isinstance(
            obj2, IPythonRunCellAction
        ):
            if (
                'edit_file_by_replace(' in obj1.code
                and 'edit_file_by_replace(' in obj2.code
            ):
                return (
                    len(obj1.code.split('\n')) > 2
                    and obj1.code.split('\n')[:3] == obj2.code.split('\n')[:3]
                )
            else:
                return obj1 == obj2
        elif isinstance(obj1, CmdOutputObservation) and isinstance(
            obj2, CmdOutputObservation
        ):
            return obj1.command == obj2.command and obj1.exit_code == obj2.exit_code
        else:
            return obj1 == obj2