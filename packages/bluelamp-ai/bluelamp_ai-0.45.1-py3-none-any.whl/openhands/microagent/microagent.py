import io
import re
from pathlib import Path
from typing import Union
import frontmatter
from pydantic import BaseModel
from openhands.core.exceptions import (
    MicroagentValidationError,
)
from openhands.core.logger import openhands_logger as logger
from openhands.microagent.types import InputMetadata, MicroagentMetadata, MicroagentType
class BaseMicroagent(BaseModel):
    """Base class for all microagents."""
    name: str
    content: str
    metadata: MicroagentMetadata
    source: str
    type: MicroagentType
    @classmethod
    def load(
        cls,
        path: Union[str, Path],
        microagent_dir: Path | None = None,
        file_content: str | None = None,
    ) -> 'BaseMicroagent':
        """Load a microagent from a markdown file with frontmatter.
        The agent's name is derived from its path relative to the microagent_dir.
        """
        path = Path(path) if isinstance(path, str) else path
        derived_name = None
        if microagent_dir is not None:
            derived_name = str(path.relative_to(microagent_dir).with_suffix(''))
        if file_content is None:
            with open(path) as f:
                file_content = f.read()
        if path.name == '.openhands_instructions':
            return RepoMicroagent(
                name='repo_legacy',
                content=file_content,
                metadata=MicroagentMetadata(name='repo_legacy'),
                source=str(path),
                type=MicroagentType.REPO_KNOWLEDGE,
            )
        file_io = io.StringIO(file_content)
        loaded = frontmatter.load(file_io)
        content = loaded.content
        metadata_dict = loaded.metadata or {}
        try:
            metadata = MicroagentMetadata(**metadata_dict)
            if metadata.mcp_tools:
                if metadata.mcp_tools.sse_servers:
                    logger.warning(
                        f'Microagent {metadata.name} has SSE servers. Only stdio servers are currently supported.'
                    )
                if not metadata.mcp_tools.stdio_servers:
                    raise MicroagentValidationError(
                        f'Microagent {metadata.name} has MCP tools configuration but no stdio servers. '
                        'Only stdio servers are currently supported.'
                    )
        except Exception as e:
            error_msg = f'Error validating microagent metadata in {path.name}: {str(e)}'
            if 'type' in metadata_dict and metadata_dict['type'] not in [
                t.value for t in MicroagentType
            ]:
                valid_types = ', '.join([f'"{t.value}"' for t in MicroagentType])
                error_msg += f'. Invalid "type" value: "{metadata_dict["type"]}". Valid types are: {valid_types}'
            raise MicroagentValidationError(error_msg) from e
        subclass_map = {
            MicroagentType.KNOWLEDGE: KnowledgeMicroagent,
            MicroagentType.REPO_KNOWLEDGE: RepoMicroagent,
            MicroagentType.TASK: TaskMicroagent,
        }
        inferred_type: MicroagentType
        if metadata.inputs:
            inferred_type = MicroagentType.TASK
            trigger = f'/{metadata.name}'
            if not metadata.triggers or trigger not in metadata.triggers:
                if not metadata.triggers:
                    metadata.triggers = [trigger]
                else:
                    metadata.triggers.append(trigger)
        elif metadata.triggers:
            inferred_type = MicroagentType.KNOWLEDGE
        else:
            inferred_type = MicroagentType.REPO_KNOWLEDGE
        if inferred_type not in subclass_map:
            raise ValueError(f'Could not determine microagent type for: {path}')
        agent_name = derived_name if derived_name is not None else metadata.name
        agent_class = subclass_map[inferred_type]
        return agent_class(
            name=agent_name,
            content=content,
            metadata=metadata,
            source=str(path),
            type=inferred_type,
        )
class KnowledgeMicroagent(BaseMicroagent):
    """Knowledge micro-agents provide specialized expertise that's triggered by keywords in conversations.
    They help with:
    - Language best practices
    - Framework guidelines
    - Common patterns
    - Tool usage
    """
    def __init__(self, **data):
        super().__init__(**data)
        if self.type not in [MicroagentType.KNOWLEDGE, MicroagentType.TASK]:
            raise ValueError('KnowledgeMicroagent must have type KNOWLEDGE or TASK')
    def match_trigger(self, message: str) -> str | None:
        """Match a trigger in the message.
        It returns the first trigger that matches the message.
        """
        message = message.lower()
        for trigger in self.triggers:
            if trigger.lower() in message:
                return trigger
        return None
    @property
    def triggers(self) -> list[str]:
        return self.metadata.triggers
class RepoMicroagent(BaseMicroagent):
    """Microagent specialized for repository-specific knowledge and guidelines.
    RepoMicroagents are loaded from `.openhands/microagents/repo.md` files within repositories
    and contain private, repository-specific instructions that are automatically loaded when
    working with that repository. They are ideal for:
        - Repository-specific guidelines
        - Team practices and conventions
        - Project-specific workflows
        - Custom documentation references
    """
    def __init__(self, **data):
        super().__init__(**data)
        if self.type != MicroagentType.REPO_KNOWLEDGE:
            raise ValueError(
                f'RepoMicroagent initialized with incorrect type: {self.type}'
            )
class TaskMicroagent(KnowledgeMicroagent):
    """TaskMicroagent is a special type of KnowledgeMicroagent that requires user input.
    These microagents are triggered by a special format: "/{agent_name}"
    and will prompt the user for any required inputs before proceeding.
    """
    def __init__(self, **data):
        super().__init__(**data)
        if self.type != MicroagentType.TASK:
            raise ValueError(
                f'TaskMicroagent initialized with incorrect type: {self.type}'
            )
        self._append_missing_variables_prompt()
    def _append_missing_variables_prompt(self) -> None:
        """Append a prompt to ask for missing variables."""
        if not self.requires_user_input() and not self.metadata.inputs:
            return
        prompt = "\n\nIf the user didn't provide any of these variables, ask the user to provide them first before the agent can proceed with the task."
        self.content += prompt
    def extract_variables(self, content: str) -> list[str]:
        """Extract variables from the content.
        Variables are in the format ${variable_name}.
        """
        pattern = r'\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}'
        matches = re.findall(pattern, content)
        return matches
    def requires_user_input(self) -> bool:
        """Check if this microagent requires user input.
        Returns True if the content contains variables in the format ${variable_name}.
        """
        variables = self.extract_variables(self.content)
        logger.debug(f'This microagent requires user input: {variables}')
        return len(variables) > 0
    @property
    def inputs(self) -> list[InputMetadata]:
        """Get the inputs for this microagent."""
        return self.metadata.inputs
def load_microagents_from_dir(
    microagent_dir: Union[str, Path],
) -> tuple[dict[str, RepoMicroagent], dict[str, KnowledgeMicroagent]]:
    """Load all microagents from the given directory.
    Note, legacy repo instructions will not be loaded here.
    Args:
        microagent_dir: Path to the microagents directory (e.g. .openhands/microagents)
    Returns:
        Tuple of (repo_agents, knowledge_agents) dictionaries
    """
    if isinstance(microagent_dir, str):
        microagent_dir = Path(microagent_dir)
    repo_agents = {}
    knowledge_agents = {}
    logger.debug(f'Loading agents from {microagent_dir}')
    if microagent_dir.exists():
        for file in microagent_dir.rglob('*.md'):
            if file.name == 'README.md':
                continue
            try:
                agent = BaseMicroagent.load(file, microagent_dir)
                if isinstance(agent, RepoMicroagent):
                    repo_agents[agent.name] = agent
                elif isinstance(agent, KnowledgeMicroagent):
                    knowledge_agents[agent.name] = agent
            except MicroagentValidationError as e:
                error_msg = f'Error loading microagent from {file}: {str(e)}'
                raise MicroagentValidationError(error_msg) from e
            except Exception as e:
                error_msg = f'Error loading microagent from {file}: {str(e)}'
                raise ValueError(error_msg) from e
    logger.debug(
        f'Loaded {len(repo_agents) + len(knowledge_agents)} microagents: '
        f'{[*repo_agents.keys(), *knowledge_agents.keys()]}'
    )
    return repo_agents, knowledge_agents