"""
BlueLamp ブランディング定義モジュール
このモジュールはBlueLamp CLIのブランディング要素（ロゴ、カラー、メッセージ）を
一元管理します。
"""
from openhands import __version__
BLUELAMP_BANNER = """
<blue>
╭─────────────────────────────────────────────────────────────────╮
│                                                                 │
│                    B L U E L A M P                              │
│                    ─────────────────                            │
│                    さあ始めましょう                             │
│                                                                 │
╰─────────────────────────────────────────────────────────────────╯
</blue>
"""
COLORS = {
    'primary': '
    'primary_light': '
    'primary_dark': '
    'secondary': '
    'info': '
    'success': '
    'warning': '
    'error': '
    'grey': '
    'light_grey': '
    'dark_grey': '
    'gold': '
}
STYLE_DICT = {
    'blue': COLORS['primary'],
    'light_blue': COLORS['primary_light'],
    'dark_blue': COLORS['primary_dark'],
    'info': COLORS['info'],
    'success': COLORS['success'],
    'warning': COLORS['warning'],
    'error': COLORS['error'],
    'grey': COLORS['grey'],
    'light_grey': COLORS['light_grey'],
    'dark_grey': COLORS['dark_grey'],
    'gold': COLORS['primary'],
    'prompt': f"{COLORS['primary']} bold",
    'selected': f"{COLORS['secondary']} bold",
    'unselected': COLORS['grey'],
}
MESSAGES = {
    'welcome': 'BlueLamp CLIへようこそ！',
    'build_prompt': '何を作りましょうか？',
    'loading_previous': '前回の会話を読み込んでいます。',
    'lets_start': 'さあ、始めましょう！',
    'agent_running': 'エージェントが実行中です...',
    'agent_paused': 'エージェントを一時停止しました。',
    'agent_finished': 'タスクが完了しました。',
    'agent_waiting': 'エージェントがあなたの入力を待っています...',
    'agent_error': 'エラーが発生しました。',
    'ctrl_c_exit': '終了しています...',
    'esc_cancel': 'ユーザーによってキャンセルされました。',
    'pausing_agent': 'エージェントを一時停止しています...',
    'confirm_action': 'このアクションを実行しますか？',
    'confirm_proceed': '続行しますか？ (h)はい/(i)いいえ/(t)つねに許可',
    'confirm_agent_handoff': 'エージェントを切り替えますか？ (h)はい/(i)いいえ/(t)つねに許可',
    'confirm_task_completion': 'タスクを完了しますか？ (h)はい/(i)いいえ/(t)つねに許可',
    'agent_switch_confirmation': 'エージェントを切り替えますか？ (h)はい/(i)いいえ/(t)つねに許可',
    'file_operation_confirmation': 'ファイル操作を実行しますか？ (h)はい/(i)いいえ/(t)つねに許可',
    'file_read_confirmation': 'ファイルを閲覧しますか？ (h)はい/(i)いいえ/(t)つねに許可',
    'file_edit_confirmation': 'ファイルを編集しますか？ (h)はい/(i)いいえ/(t)つねに許可',
    'command_execution_confirmation': 'コマンドを実行しますか？ (h)はい/(i)いいえ/(t)つねに許可',
    'confirm_yes': 'はい',
    'confirm_no': 'いいえ',
    'confirm_always': 'つねに許可',
    'no_settings': '設定が見つかりません。初期設定を開始します...',
    'setup_complete': '設定が完了しました！',
    'setup_failed': '設定に失敗しました。',
    'command_help': 'ヘルプ',
    'command_status': 'ステータス',
    'command_settings': '設定',
    'command_clear': 'クリア',
    'command_exit': '終了',
    'command_save': '保存',
    'command_load': '読み込み',
    'error_connection': '接続エラー: {error}',
    'error_generic': 'エラーが発生しました: {error}',
    'error_invalid_command': '無効なコマンドです: {command}',
    'error_file_not_found': 'ファイルが見つかりません: {file}',
    'info_saving': '保存中...',
    'info_loading': '読み込み中...',
    'info_connecting': '接続中...',
    'info_initializing': '初期化中...',
    'prompt_continue': '続けますか？',
    'prompt_enter_command': 'コマンドを入力してください: ',
    'prompt_select_option': 'オプションを選択してください: ',
    'session_id': 'セッションID: {sid}',
    'session_resumed': 'セッション {sid} を再開しました',
    'session_error_recovery': '注意: 前回のセッションはエラーで終了しました。タスクを再開せず、状況を確認してください。',
    'task_completed': 'タスクが完了しました: {task}',
    'task_in_progress': 'タスクを実行中: {task}',
    'task_failed': 'タスクが失敗しました: {task}',
    'press_key_continue': '続けるには任意のキーを押してください...',
    'shutting_down': 'シャットダウン中...',
    'portal_auth_required': 'Portal認証が必要です。',
    'portal_auth_prompt': 'Portalアカウントでログインしてください。',
    'portal_auth_success': '認証成功: {name} としてログインしました。',
    'portal_auth_error': '認証エラー: {error}',
    'portal_network_error': 'ネットワークエラー: {error}',
    'portal_auth_cancelled': '認証がキャンセルされました。',
    'portal_authenticated': '認証済み: {name} としてログイン中',
    'portal_key_invalid': 'APIキーが無効化されています。新しいキーを入力してください。',
    'portal_connection_error': '警告: Portal接続エラー - {error}',
    'portal_offline_mode': 'オフラインモードで続行します。',
    'portal_auth_check_failed': '認証エラー: APIキーが無効化されました。現在のタスク完了後に終了します。',
    'portal_retry_prompt': 'もう一度試すか、Ctrl+Cで終了してください。',
    'portal_connection_check': 'Portal接続を確認してください。',
}
COMMAND_DESCRIPTIONS = {
    '/help': 'ヘルプを表示',
    '/status': '現在の状態を表示',
    '/settings': '設定画面を開く',
    '/clear': '画面をクリア',
    '/exit': 'BlueLamp CLIを終了',
    '/logout': 'ログアウトして認証情報をクリア',
    '/save': '現在のセッションを保存',
    '/load': '保存されたセッションを読み込み',
    '/stop': 'エージェントを停止',
    '/resume': 'エージェントを再開',
}
SETTINGS_LABELS = {
    'title': 'BlueLamp CLI 設定',
    'model': 'AIモデル',
    'api_key': 'APIキー',
    'temperature': '生成温度',
    'max_tokens': '最大トークン数',
    'save': '保存',
    'cancel': 'キャンセル',
    'reset': 'リセット',
    'advanced': '詳細設定',
    'basic': '基本設定',
}
def get_message(key: str, target_agent_name: str = None, current_agent_name: str = None, **kwargs) -> str:
    """
    メッセージキーから日本語メッセージを取得
    Args:
        key: メッセージキー
        target_agent_name: 切り替え先エージェント名（動的メッセージ生成用）
        current_agent_name: 現在のエージェント名（動的メッセージ生成用）
        **kwargs: フォーマット用の引数
    Returns:
        フォーマットされたメッセージ
    """
    if key == 'confirm_task_completion' and target_agent_name:
        if current_agent_name == 'OrchestrationAgent':
            return f'{target_agent_name}に依頼しますか？ (h)はい/(i)いいえ/(t)つねに許可'
        elif target_agent_name == 'OrchestrationAgent':
            return f'オーケストレーターに戻りますか？ (h)はい/(i)いいえ/(t)つねに許可'
        else:
            return f'{target_agent_name}に切り替えますか？ (h)はい/(i)いいえ/(t)つねに許可'
    message = MESSAGES.get(key, key)
    if kwargs:
        return message.format(**kwargs)
    return message
def get_color(key: str) -> str:
    """
    カラーキーから色コードを取得
    Args:
        key: カラーキー
    Returns:
        色コード（16進数）
    """
    return COLORS.get(key, COLORS['primary'])