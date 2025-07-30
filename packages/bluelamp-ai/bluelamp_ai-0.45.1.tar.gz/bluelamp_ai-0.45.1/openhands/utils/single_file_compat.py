"""
Single File Compatibility Helper
単一ファイル実行時の互換性を保つヘルパー
"""
import os
import sys
from pathlib import Path
def get_resource_path(relative_path: str) -> Path:
    """
    リソースファイルの正しいパスを取得
    PyInstallerでパッケージ化されていても動作する
    """
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    if "__compiled__" in globals():
        return Path(sys.argv[0]).parent / relative_path
    return Path(__file__).parent.parent / relative_path
def is_frozen() -> bool:
    """単一ファイル化されているかチェック"""
    return hasattr(sys, '_MEIPASS') or "__compiled__" in globals()
def get_app_data_dir() -> Path:
    """アプリケーションデータディレクトリを取得"""
    if is_frozen():
        if sys.platform == "win32":
            base = Path(os.environ.get('APPDATA', ''))
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path.home() / ".local" / "share"
        return base / "bluelamp"
    else:
        return Path.cwd() / ".bluelamp"
def get_temp_dir() -> Path:
    """一時ディレクトリを取得"""
    if is_frozen():
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS) / "temp"
    import tempfile
    return Path(tempfile.gettempdir()) / "bluelamp"
class CompatibleObscureStorage:
    """単一ファイル対応の隠蔽ストレージ"""
    def __init__(self):
        self.base_path = get_app_data_dir() / "sessions"
        self.base_path.mkdir(parents=True, exist_ok=True)
    def get_api_key_path(self) -> Path:
        """APIキーファイルのパスを取得"""
        return self.base_path / "2874fd16-7e86-4c34-98ac-d2cfb3f62478-d5e2b751df612560" / "events" / "1.json"