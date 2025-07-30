"""
Portal連携PromptManager
Portal APIからプロンプトを取得する機能を持つPromptManager
"""
import os
import asyncio
import logging
from typing import Optional, TYPE_CHECKING
from jinja2 import Template
from .prompt_client import PortalPromptClient
from .prompt_mapping import is_portal_prompt, get_prompt_id
if TYPE_CHECKING:
    from openhands.controller.state.state import State
    from openhands.core.message import Message
logger = logging.getLogger('bluelamp.portal.prompt_manager')
class PortalPromptManager:
    """Portal APIからプロンプトを取得するPromptManager"""
    def __init__(
        self,
        prompt_dir: str,
        system_prompt_filename: str = 'system_prompt.j2',
        portal_base_url: Optional[str] = None,
        enable_portal: bool = True
    ):
        """
        Args:
            prompt_dir: ローカルプロンプトディレクトリ
            system_prompt_filename: システムプロンプトファイル名
            portal_base_url: PortalのベースURL
            enable_portal: Portal連携を有効にするか
        """
        self.prompt_dir = prompt_dir
        self.system_prompt_filename = system_prompt_filename
        self.portal_client = PortalPromptClient(base_url=portal_base_url) if enable_portal else None
        self.enable_portal = enable_portal
        self._portal_content_cache: Optional[str] = None
        self._local_manager = None
        template_dir = os.path.dirname(__file__)
        self._additional_info_template = None
        additional_info_path = os.path.join(template_dir, 'additional_info.j2')
        if os.path.exists(additional_info_path):
            with open(additional_info_path, 'r') as f:
                self._additional_info_template = Template(f.read())
        self._user_template = None
        user_prompt_path = os.path.join(template_dir, 'user_prompt.j2')
        if os.path.exists(user_prompt_path):
            with open(user_prompt_path, 'r') as f:
                self._user_template = Template(f.read())
        logger.info(f"PortalPromptManager初期化: portal={enable_portal}, file={system_prompt_filename}")
    def _get_local_manager(self):
        """ローカルPromptManagerを遅延初期化"""
        if self._local_manager is None:
            from openhands.utils.prompt import PromptManager
            self._local_manager = PromptManager(
                prompt_dir=self.prompt_dir,
                system_prompt_filename=self.system_prompt_filename
            )
        return self._local_manager
    async def _fetch_portal_content(self, retry_on_auth_error: bool = True) -> Optional[str]:
        """Portal APIからプロンプト内容を取得"""
        if not self.enable_portal or not self.portal_client:
            return None
        try:
            if not is_portal_prompt(self.system_prompt_filename):
                logger.debug(f"Portal連携対象外: {self.system_prompt_filename}")
                return None
            content = await self.portal_client.fetch_prompt_by_filename(self.system_prompt_filename)
            if content:
                logger.info(f"Portal プロンプト取得成功: {self.system_prompt_filename}")
                return content
            else:
                logger.warning(f"Portal プロンプト取得失敗: {self.system_prompt_filename}")
                if retry_on_auth_error:
                    logger.info("認証エラーの可能性があります。自動再認証を試行します...")
                    try:
                        from openhands.cli.auth import PortalAuthenticator
                        auth = PortalAuthenticator()
                        auth.load_api_key()
                        try:
                            await auth.verify_api_key(auto_reauth=True)
                            logger.info("再認証後にプロンプト取得を再試行します...")
                            return await self._fetch_portal_content(retry_on_auth_error=False)
                        except Exception as auth_error:
                            logger.error(f"自動再認証に失敗: {auth_error}")
                            return None
                    except Exception as reauth_error:
                        logger.error(f"再認証処理エラー: {reauth_error}")
                        return None
                return None
        except Exception as e:
            logger.error(f"Portal プロンプト取得エラー: {e}")
            if retry_on_auth_error and ("401" in str(e) or "unauthorized" in str(e).lower() or "authentication" in str(e).lower()):
                logger.info("認証エラーを検出しました。自動再認証を試行します...")
                try:
                    from openhands.cli.auth import PortalAuthenticator
                    auth = PortalAuthenticator()
                    auth.load_api_key()
                    try:
                        await auth.verify_api_key(auto_reauth=True)
                        logger.info("再認証後にプロンプト取得を再試行します...")
                        return await self._fetch_portal_content(retry_on_auth_error=False)
                    except Exception as auth_error:
                        logger.error(f"自動再認証に失敗: {auth_error}")
                        return None
                except Exception as reauth_error:
                    logger.error(f"再認証処理エラー: {reauth_error}")
                    return None
            return None
    def get_system_message(self) -> str:
        """
        システムメッセージを取得
        Portal優先、ローカルフォールバック
        """
        try:
            if self._portal_content_cache is not None:
                logger.debug("キャッシュからプロンプトを返却")
                return self._clean_portal_prompt(self._portal_content_cache)
            if self.enable_portal and is_portal_prompt(self.system_prompt_filename):
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, self._fetch_portal_content())
                            portal_content = future.result(timeout=10)
                    else:
                        portal_content = asyncio.run(self._fetch_portal_content())
                    if portal_content:
                        self._portal_content_cache = portal_content
                        logger.info(f"Portal プロンプト使用: {self.system_prompt_filename}")
                        return self._clean_portal_prompt(portal_content)
                except Exception as e:
                    logger.warning(f"Portal プロンプト取得失敗、ローカルにフォールバック: {e}")
            logger.info(f"ローカル プロンプト使用: {self.system_prompt_filename}")
            local_manager = self._get_local_manager()
            return local_manager.get_system_message()
        except Exception as e:
            logger.error(f"プロンプト取得エラー: {e}")
            return "
    async def get_system_message_async(self) -> str:
        """
        非同期でシステムメッセージを取得
        """
        try:
            if self._portal_content_cache is not None:
                logger.debug("キャッシュからプロンプトを返却")
                return self._clean_portal_prompt(self._portal_content_cache)
            if self.enable_portal and is_portal_prompt(self.system_prompt_filename):
                portal_content = await self._fetch_portal_content()
                if portal_content:
                    self._portal_content_cache = portal_content
                    logger.info(f"Portal プロンプト使用: {self.system_prompt_filename}")
                    return self._clean_portal_prompt(portal_content)
            logger.info(f"ローカル プロンプト使用: {self.system_prompt_filename}")
            local_manager = self._get_local_manager()
            return local_manager.get_system_message()
        except Exception as e:
            logger.error(f"プロンプト取得エラー: {e}")
            return "
    def _clean_portal_prompt(self, content: str) -> str:
        """
        Portalから取得したプロンプトをクリーンアップ
        - メタデータ（Source、Fetchedなど）を削除
        - {{ instructions }}などのテンプレート変数を処理
        """
        try:
            if "\n---\n" in content:
                content = content.split("\n---\n")[0]
            content = content.replace("{{ instructions }}", "")
            return content.strip()
        except Exception as e:
            logger.error(f"プロンプトクリーンアップエラー: {e}")
            return content
    def clear_cache(self):
        """プロンプトキャッシュをクリア"""
        self._portal_content_cache = None
        logger.debug("プロンプトキャッシュをクリアしました")
    async def test_portal_connection(self) -> bool:
        """Portal接続テスト"""
        if not self.enable_portal or not self.portal_client:
            return False
        return await self.portal_client.test_connection()
    def get_example_user_message(self) -> str:
        """ユーザーメッセージ例を取得"""
        if self._user_template:
            try:
                return self._user_template.render().strip()
            except Exception as e:
                logger.error(f"user_prompt テンプレートレンダリングエラー: {e}")
                return ""
        else:
            local_manager = self._get_local_manager()
            return local_manager.get_example_user_message()
    def get_user_message(self, task: str, **kwargs) -> str:
        """ユーザーメッセージを取得（ローカルから）"""
        local_manager = self._get_local_manager()
        return local_manager.get_user_message(task, **kwargs)
    def build_workspace_context(
        self,
        repository_info=None,
        runtime_info=None,
        conversation_instructions=None,
        repo_instructions: str = '',
    ) -> str:
        """ワークスペースコンテキストを構築"""
        if self._additional_info_template:
            try:
                context = self._additional_info_template.render(
                    repository_info=repository_info,
                    repository_instructions=repo_instructions,
                    runtime_info=runtime_info,
                    conversation_instructions=conversation_instructions,
                )
                return context.strip()
            except Exception as e:
                logger.error(f"additional_info テンプレートレンダリングエラー: {e}")
                return ""
        else:
            local_manager = self._get_local_manager()
            return local_manager.build_workspace_context(
                repository_info=repository_info,
                runtime_info=runtime_info,
                conversation_instructions=conversation_instructions,
                repo_instructions=repo_instructions,
            )
    def build_microagent_info(self, triggered_agents=None) -> str:
        """マイクロエージェント情報を構築"""
        return ""
    def add_turns_left_reminder(self, messages: list['Message'], state: 'State') -> None:
        """残りターン数のリマインダーをメッセージに追加"""
        local_manager = self._get_local_manager()
        local_manager.add_turns_left_reminder(messages, state)
def create_portal_prompt_manager(
    prompt_dir: str,
    system_prompt_filename: str = 'system_prompt.j2',
    portal_base_url: Optional[str] = None,
    enable_portal: bool = True
) -> PortalPromptManager:
    """PortalPromptManagerを作成する便利関数"""
    return PortalPromptManager(
        prompt_dir=prompt_dir,
        system_prompt_filename=system_prompt_filename,
        portal_base_url=portal_base_url,
        enable_portal=enable_portal
    )
async def test_portal_prompt_manager():
    """PortalPromptManagerのテスト"""
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as temp_dir:
        test_prompt_path = os.path.join(temp_dir, 'feature_extension.j2')
        with open(test_prompt_path, 'w') as f:
            f.write("
        manager = PortalPromptManager(
            prompt_dir=temp_dir,
            system_prompt_filename='feature_extension.j2',
            enable_portal=True
        )
        print("Portal接続テスト...")
        if await manager.test_portal_connection():
            print("✅ Portal接続成功")
        else:
            print("❌ Portal接続失敗")
        print("\nプロンプト取得テスト...")
        content = await manager.get_system_message_async()
        print(f"取得したプロンプト: {len(content)}文字")
        print(f"内容プレビュー: {content[:100]}...")
if __name__ == "__main__":
    asyncio.run(test_portal_prompt_manager())