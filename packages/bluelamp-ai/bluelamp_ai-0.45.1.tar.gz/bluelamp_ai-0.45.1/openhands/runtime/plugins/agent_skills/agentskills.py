from inspect import signature
from openhands.runtime.plugins.agent_skills import file_ops, file_reader
from openhands.runtime.plugins.agent_skills.utils.dependency import import_functions
import_functions(
    module=file_ops, function_names=file_ops.__all__, target_globals=globals()
)
import_functions(
    module=file_reader, function_names=file_reader.__all__, target_globals=globals()
)
__all__ = file_ops.__all__ + file_reader.__all__
try:
    from openhands.runtime.plugins.agent_skills import repo_ops
    import_functions(
        module=repo_ops, function_names=repo_ops.__all__, target_globals=globals()
    )
    __all__ += repo_ops.__all__
except ImportError:
    pass
DOCUMENTATION = ''
for func_name in __all__:
    func = globals()[func_name]
    cur_doc = func.__doc__
    cur_doc = '\n'.join(filter(None, map(lambda x: x.strip(), cur_doc.split('\n'))))
    cur_doc = '\n'.join(map(lambda x: ' ' * 4 + x, cur_doc.split('\n')))
    fn_signature = f'{func.__name__}' + str(signature(func))
    DOCUMENTATION += f'{fn_signature}:\n{cur_doc}\n\n'
from openhands.runtime.plugins.agent_skills.file_editor import file_editor
__all__ += ['file_editor']