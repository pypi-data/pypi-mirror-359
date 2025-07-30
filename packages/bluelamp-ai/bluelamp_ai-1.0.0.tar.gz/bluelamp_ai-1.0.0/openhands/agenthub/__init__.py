try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # PyInstaller環境では.envファイルは使用しない
    pass


from openhands.agenthub import (  # noqa: E402
    codeact_agent,  # BlueLampOrchestrator
    bluelamp_agents,  # 16専門エージェント
)
from openhands.controller.agent import Agent  # noqa: E402

__all__ = [
    'Agent',
    'codeact_agent',  # BlueLampOrchestrator
    'bluelamp_agents',  # 16専門エージェント
]
