from enum import Enum
from pydantic import BaseModel, Field
from openhands.core.config.mcp_config import (
    MCPConfig,
)
class MicroagentType(str, Enum):
    """Type of microagent."""
    KNOWLEDGE = 'knowledge'
    REPO_KNOWLEDGE = 'repo'
    TASK = 'task'
class InputMetadata(BaseModel):
    """Metadata for task microagent inputs."""
    name: str
    description: str
class MicroagentMetadata(BaseModel):
    """Metadata for all microagents."""
    name: str = 'default'
    type: MicroagentType = Field(default=MicroagentType.REPO_KNOWLEDGE)
    version: str = Field(default='1.0.0')
    agent: str = Field(default='CodeActAgent')
    triggers: list[str] = []
    inputs: list[InputMetadata] = []
    mcp_tools: MCPConfig | None = (
        None
    )