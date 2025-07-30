from __future__ import annotations
from contextlib import contextmanager
from openhands.controller.state.state import State
from openhands.core.config.condenser_config import CondenserPipelineConfig
from openhands.memory.condenser.condenser import Condensation, Condenser
from openhands.memory.view import View
class CondenserPipeline(Condenser):
    """Combines multiple condensers into a single condenser.
    This is useful for creating a pipeline of condensers that can be chained together to achieve very specific condensation aims. Each condenser is run in sequence, passing the output view of one to the next, until we reach the end or a `CondensationAction` is returned instead.
    """
    def __init__(self, *condenser: Condenser) -> None:
        self.condensers = list(condenser)
        super().__init__()
    @contextmanager
    def metadata_batch(self, state: State):
        try:
            yield
        finally:
            for condenser in self.condensers:
                condenser.write_metadata(state)
    def condense(self, view: View) -> View | Condensation:
        result: View | Condensation = view
        for condenser in self.condensers:
            result = condenser.condense(result)
            if isinstance(result, Condensation):
                break
        return result
    @classmethod
    def from_config(cls, config: CondenserPipelineConfig) -> CondenserPipeline:
        condensers = [Condenser.from_config(c) for c in config.condensers]
        return CondenserPipeline(*condensers)
CondenserPipeline.register_config(CondenserPipelineConfig)