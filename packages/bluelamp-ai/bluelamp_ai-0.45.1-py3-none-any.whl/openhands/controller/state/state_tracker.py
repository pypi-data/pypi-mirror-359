from openhands.controller.agent import Agent
from openhands.controller.state.control_flags import (
    BudgetControlFlag,
    IterationControlFlag,
)
from openhands.controller.state.state import State
from openhands.core.logger import openhands_logger as logger
from openhands.events.action.agent import AgentDelegateAction, ChangeAgentStateAction
from openhands.events.action.empty import NullAction
from openhands.events.event import Event
from openhands.events.event_filter import EventFilter
from openhands.events.observation.agent import AgentStateChangedObservation
from openhands.events.observation.delegate import AgentDelegateObservation
from openhands.events.observation.empty import NullObservation
from openhands.events.serialization.event import event_to_trajectory
from openhands.events.stream import EventStream
from openhands.llm.metrics import Metrics
from openhands.storage.files import FileStore
class StateTracker:
    """Manages and synchronizes the state of an agent throughout its lifecycle.
    It is responsible for:
    1. Maintaining agent state persistence across sessions
    2. Managing agent history by filtering and tracking relevant events (previously done in the agent controller)
    3. Synchronizing metrics between the controller and LLM components
    4. Updating control flags for budget and iteration limits
    """
    def __init__(
        self, sid: str | None, file_store: FileStore | None, user_id: str | None
    ):
        self.sid = sid
        self.file_store = file_store
        self.user_id = user_id
        self.agent_history_filter = EventFilter(
            exclude_types=(
                NullAction,
                NullObservation,
                ChangeAgentStateAction,
                AgentStateChangedObservation,
            ),
            exclude_hidden=True,
        )
    def set_initial_state(
        self,
        id: str,
        agent: Agent,
        state: State | None,
        max_iterations: int,
        max_budget_per_task: float | None,
        confirmation_mode: bool = False,
    ) -> None:
        """Sets the initial state for the agent, either from the previous session, or from a parent agent, or by creating a new one.
        Args:
            state: The state to initialize with, or None to create a new state.
            max_iterations: The maximum number of iterations allowed for the task.
            confirmation_mode: Whether to enable confirmation mode.
        """
        if state is None:
            self.state = State(
                session_id=id.removesuffix('-delegate'),
                inputs={},
                iteration_flag=IterationControlFlag(
                    limit_increase_amount=max_iterations,
                    current_value=0,
                    max_value=max_iterations,
                ),
                budget_flag=None
                if not max_budget_per_task
                else BudgetControlFlag(
                    limit_increase_amount=max_budget_per_task,
                    current_value=0,
                    max_value=max_budget_per_task,
                ),
                confirmation_mode=confirmation_mode,
            )
            self.state.start_id = 0
            logger.info(
                f'AgentController {id} - created new state. start_id: {self.state.start_id}'
            )
        else:
            self.state = state
            if self.state.start_id <= -1:
                self.state.start_id = 0
            logger.info(
                f'AgentController {id} initializing history from event {self.state.start_id}',
            )
        agent.llm.metrics = self.state.metrics
    def _init_history(self, event_stream: EventStream) -> None:
        """Initializes the agent's history from the event stream.
        The history is a list of events that:
        - Excludes events of types listed in self.filter_out
        - Excludes events with hidden=True attribute
        - For delegate events (between AgentDelegateAction and AgentDelegateObservation):
            - Excludes all events between the action and observation
            - Includes the delegate action and observation themselves
        """
        start_id = self.state.start_id if self.state.start_id >= 0 else 0
        end_id = (
            self.state.end_id
            if self.state.end_id >= 0
            else event_stream.get_latest_event_id()
        )
        if start_id > end_id + 1:
            logger.warning(
                f'start_id {start_id} is greater than end_id + 1 ({end_id + 1}). History will be empty.',
            )
            self.state.history = []
            return
        events: list[Event] = []
        events_to_add = list(
            event_stream.search_events(
                start_id=start_id,
                end_id=end_id,
                reverse=False,
                filter=self.agent_history_filter,
            )
        )
        events.extend(events_to_add)
        delegate_ranges: list[tuple[int, int]] = []
        delegate_action_ids: list[int] = []
        for event in events:
            if isinstance(event, AgentDelegateAction):
                delegate_action_ids.append(event.id)
            elif isinstance(event, AgentDelegateObservation):
                if not delegate_action_ids:
                    logger.warning(
                        f'Found AgentDelegateObservation without matching action at id={event.id}',
                    )
                    continue
                action_id = delegate_action_ids.pop()
                delegate_ranges.append((action_id, event.id))
        if delegate_ranges:
            filtered_events: list[Event] = []
            current_idx = 0
            for start_id, end_id in sorted(delegate_ranges):
                filtered_events.extend(
                    event for event in events[current_idx:] if event.id < start_id
                )
                filtered_events.extend(
                    event for event in events if event.id in (start_id, end_id)
                )
                current_idx = next(
                    (i for i, e in enumerate(events) if e.id > end_id), len(events)
                )
            filtered_events.extend(events[current_idx:])
            self.state.history = filtered_events
        else:
            self.state.history = events
        self.state.start_id = start_id
    def close(self, event_stream: EventStream):
        start_id = self.state.start_id if self.state.start_id >= 0 else 0
        end_id = (
            self.state.end_id
            if self.state.end_id >= 0
            else event_stream.get_latest_event_id()
        )
        self.state.history = list(
            event_stream.search_events(
                start_id=start_id,
                end_id=end_id,
                reverse=False,
                filter=self.agent_history_filter,
            )
        )
    def add_history(self, event: Event):
        if self.agent_history_filter.include(event):
            self.state.history.append(event)
    def get_trajectory(self, include_screenshots: bool = False) -> list[dict]:
        return [
            event_to_trajectory(event, include_screenshots)
            for event in self.state.history
        ]
    def maybe_increase_control_flags_limits(self, headless_mode: bool):
        self.state.iteration_flag.increase_limit(headless_mode)
        if self.state.budget_flag:
            self.state.budget_flag.increase_limit(headless_mode)
    def get_metrics_snapshot(self):
        """
        Deep copy of metrics
        This serves as a snapshot for the parent's metrics at the time a delegate is created
        It will be stored and used to compute local metrics for the delegate
        (since delegates now accumulate metrics from where its parent left off)
        """
        return self.state.metrics.copy()
    def save_state(self):
        """
        Save's current state to persistent store
        """
        if self.sid and self.file_store:
            self.state.save_to_session(self.sid, self.file_store, self.user_id)
    def run_control_flags(self):
        """
        Performs one step of the control flags
        """
        self.state.iteration_flag.step()
        if self.state.budget_flag:
            self.state.budget_flag.step()
    def sync_budget_flag_with_metrics(self):
        """
        Ensures that budget flag is up to date with accumulated costs from llm completions
        Budget flag will monitor for when budget is exceeded
        """
        if self.state.budget_flag:
            self.state.budget_flag.current_value = self.state.metrics.accumulated_cost
    def merge_metrics(self, metrics: Metrics):
        """
        Merges metrics with the state metrics
        NOTE: this should be refactored in the future. We should have services (draft llm, title autocomplete, condenser, etc)
        use their own LLMs, but the metrics object should be shared. This way we have one source of truth for accumulated costs from
        all services
        This would prevent having fragmented stores for metrics, and we don't have the burden of deciding where and how to store them
        if we decide introduce more specialized services that require llm completions
        """
        self.state.metrics.merge(metrics)
        if self.state.budget_flag:
            self.state.budget_flag.current_value = self.state.metrics.accumulated_cost