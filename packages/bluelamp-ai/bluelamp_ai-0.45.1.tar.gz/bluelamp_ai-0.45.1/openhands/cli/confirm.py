"""
軽量なユーザー確認機能
状態管理やイベントストリームを使わない、シンプルな実装
"""
import asyncio
import sys
from typing import Optional
async def get_user_confirmation(
    message: str, 
    default: bool = True,
    timeout: Optional[float] = 30.0
) -> bool:
    """
    ユーザーに確認を求める（軽量版）
    Args:
        message: 確認メッセージ
        default: デフォルトの選択（タイムアウト時に使用）
        timeout: タイムアウト時間（秒）、Noneで無制限
    Returns:
        True: ユーザーが承認
        False: ユーザーが拒否
    """
    print(f"\n{message}")
    default_text = "Y/n" if default else "y/N"
    print(f"続行しますか？ ({default_text}): ", end='', flush=True)
    try:
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, sys.stdin.readline)
        if timeout:
            response = await asyncio.wait_for(future, timeout=timeout)
        else:
            response = await future
        response = response.strip().lower()
        if response == '':
            return default
        return response in ['y', 'yes', 'はい', 'h']
    except asyncio.TimeoutError:
        print(f"\n(タイムアウト - {'続行' if default else 'キャンセル'}します)")
        return default
    except KeyboardInterrupt:
        print("\n(中断されました)")
        return False
    except Exception as e:
        print(f"\n(エラー: {e} - {'続行' if default else 'キャンセル'}します)")
        return default
def format_agent_switch_message(
    from_agent: str,
    to_agent: str,
    task: str,
    max_task_length: int = 100
) -> str:
    """
    エージェント切り替え確認メッセージをフォーマット
    """
    if len(task) > max_task_length:
        task = task[:max_task_length-3] + "..."
    return f"""
╭─── エージェント切り替え確認 ───╮
│ 現在: {from_agent}
│ 切替先: {to_agent}
│ タスク: {task}
╰─────────────────────────────╯"""