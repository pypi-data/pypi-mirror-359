from openhands.runtime.base import Runtime
from openhands.runtime.impl.cli.cli_runtime import CLIRuntime
from openhands.runtime.impl.docker.docker_runtime import (
    DockerRuntime,
)
from openhands.runtime.impl.e2b.e2b_runtime import E2BRuntime
from openhands.runtime.impl.local.local_runtime import LocalRuntime
from openhands.runtime.impl.remote.remote_runtime import RemoteRuntime
from openhands.utils.import_utils import get_impl

# Optional runtime imports - only available if dependencies are installed
try:
    from openhands.runtime.impl.daytona.daytona_runtime import DaytonaRuntime
except ImportError:
    DaytonaRuntime = None

try:
    from openhands.runtime.impl.kubernetes.kubernetes_runtime import KubernetesRuntime
except ImportError:
    KubernetesRuntime = None

try:
    from openhands.runtime.impl.modal.modal_runtime import ModalRuntime
except ImportError:
    ModalRuntime = None

try:
    from openhands.runtime.impl.runloop.runloop_runtime import RunloopRuntime
except ImportError:
    RunloopRuntime = None

# mypy: disable-error-code="type-abstract"
_DEFAULT_RUNTIME_CLASSES: dict[str, type[Runtime]] = {
    'eventstream': DockerRuntime,
    'docker': DockerRuntime,
    'e2b': E2BRuntime,
    'remote': RemoteRuntime,
    'local': LocalRuntime,
    'cli': CLIRuntime,
}

# Add optional runtimes if available
if ModalRuntime is not None:
    _DEFAULT_RUNTIME_CLASSES['modal'] = ModalRuntime
if RunloopRuntime is not None:
    _DEFAULT_RUNTIME_CLASSES['runloop'] = RunloopRuntime
if DaytonaRuntime is not None:
    _DEFAULT_RUNTIME_CLASSES['daytona'] = DaytonaRuntime
if KubernetesRuntime is not None:
    _DEFAULT_RUNTIME_CLASSES['kubernetes'] = KubernetesRuntime


def get_runtime_cls(name: str) -> type[Runtime]:
    """
    If name is one of the predefined runtime names (e.g. 'docker'), return its class.
    Otherwise attempt to resolve name as subclass of Runtime and return it.
    Raise on invalid selections.
    """
    if name in _DEFAULT_RUNTIME_CLASSES:
        return _DEFAULT_RUNTIME_CLASSES[name]
    try:
        return get_impl(Runtime, name)
    except Exception as e:
        known_keys = _DEFAULT_RUNTIME_CLASSES.keys()
        raise ValueError(
            f'Runtime {name} not supported, known are: {known_keys}'
        ) from e


__all__ = [
    'Runtime',
    'E2BRuntime',
    'RemoteRuntime',
    'DockerRuntime',
    'CLIRuntime',
    'get_runtime_cls',
]

# Add optional runtime classes to __all__ if available
if ModalRuntime is not None:
    __all__.append('ModalRuntime')
if RunloopRuntime is not None:
    __all__.append('RunloopRuntime')
if DaytonaRuntime is not None:
    __all__.append('DaytonaRuntime')
if KubernetesRuntime is not None:
    __all__.append('KubernetesRuntime')
