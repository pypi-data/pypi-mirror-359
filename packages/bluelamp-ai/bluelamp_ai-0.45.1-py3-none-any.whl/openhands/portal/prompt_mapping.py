"""
プロンプトマッピング設定
ローカルプロンプトファイル名とPortal側プロンプトIDのマッピング
"""
PROMPT_MAPPING = {
    'refactoring_expert.j2': '6862397f1428c1efc592f6ec',
    'data_modeling_engineer.j2': '6862397f1428c1efc592f6d2',
    'feature_extension.j2': '6862397f1428c1efc592f6ea',
    'system_architect.j2': '6862397f1428c1efc592f6d4',
    'debug_detective.j2': '6862397f1428c1efc592f6e2',
    'environment_setup.j2': '6862397f1428c1efc592f6d8',
    'ui_ux_designer.j2': '6862397f1428c1efc592f6d0',
    'test_quality_verification.j2': '6862397f1428c1efc592f6de',
    'github_manager.j2': '6862397f1428c1efc592f6e6',
    'typescript_manager.j2': '6862397f1428c1efc592f6e8',
    'orchestrator.j2': '6862397f1428c1efc592f6cc',
    'backend_implementation.j2': '6862397f1428c1efc592f6dc',
    'deploy_specialist.j2': '6862397f1428c1efc592f6e4',
    'api_integration.j2': '6862397f1428c1efc592f6e0',
    'implementation_consultant.j2': '6862397f1428c1efc592f6d6',
    'prototype_implementation.j2': '6862397f1428c1efc592f6da',
    'requirements_engineer.j2': '6862397f1428c1efc592f6ce',
    'system_prompt.j2': '6862397f1428c1efc592f6cc',
}
ID_TO_LOCAL = {v: k for k, v in PROMPT_MAPPING.items()}
PROMPT_TITLES = {
    '6862397f1428c1efc592f6ec': '
    '6862397f1428c1efc592f6d2': '
    '6862397f1428c1efc592f6ea': '
    '6862397f1428c1efc592f6d4': '
    '6862397f1428c1efc592f6e2': '
    '6862397f1428c1efc592f6d8': '
    '6862397f1428c1efc592f6d0': '
    '6862397f1428c1efc592f6de': '
    '6862397f1428c1efc592f6e6': '
    '6862397f1428c1efc592f6e8': '
    '6862397f1428c1efc592f6cc': '
    '6862397f1428c1efc592f6dc': '
    '6862397f1428c1efc592f6e4': '
    '6862397f1428c1efc592f6e0': '
    '6862397f1428c1efc592f6d6': '
    '6862397f1428c1efc592f6da': '
    '6862397f1428c1efc592f6ce': '
}
def get_prompt_id(local_filename: str) -> str:
    """ローカルファイル名からPortal プロンプトIDを取得"""
    return PROMPT_MAPPING.get(local_filename)
def get_local_filename(prompt_id: str) -> str:
    """Portal プロンプトIDからローカルファイル名を取得"""
    return ID_TO_LOCAL.get(prompt_id)
def get_prompt_title(prompt_id: str) -> str:
    """Portal プロンプトIDからタイトルを取得"""
    return PROMPT_TITLES.get(prompt_id, 'Unknown Prompt')
def is_portal_prompt(local_filename: str) -> bool:
    """ローカルファイル名がPortal連携対象かチェック"""
    return local_filename in PROMPT_MAPPING