from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Callable, Optional, Pattern

@dataclass
class Command:
   pattern: Pattern[str]
   action_name: str
   handler: Callable  # handler(deps, match) -> str | None

def _say(deps, text: str) -> None:
    """
    可選：如果你有本地 TTS/或用 realtime 回音訊，這裡先留空。
    在此 repo 多半是由 realtime 模型負責說話，
    所以可以回傳一段文字讓上層決定是否送給模型朗讀。
    """
    # no-op by default
    return None

def build_commands():
    # 你可以把關鍵字做得更嚴謹：用 regex + 同義詞
    return [
        Command(
            pattern=re.compile(r"(跳舞|dance)", re.I),
            action_name="dance",
            handler=lambda deps, m: deps.movement_manager.dance() or "收到！我來跳舞～",
        ),
        Command(
            pattern=re.compile(r"(點頭|nod)", re.I),
            action_name="nod",
            handler=lambda deps, m: deps.movement_manager.nod() or "好的，我點頭。",
        ),
        Command(
            pattern=re.compile(r"(看這裡|看前面|look\s*at\s*me)", re.I),
            action_name="look_at_me",
            handler=lambda deps, m: deps.movement_manager.look_at_user() or "我看向你了。",
        ),
        Command(
            pattern=re.compile(r"(停止|停下|stop)", re.I),
            action_name="stop",
            handler=lambda deps, m: deps.movement_manager.stop_all() or "已停止動作。",
        ),
        # 例：帶參數的命令：轉頭 30 度
        Command(
            pattern=re.compile(r"(轉頭|rotate)\s*(-?\d+)", re.I),
            action_name="rotate_head",
            handler=lambda deps, m: deps.movement_manager.rotate_head(yaw_deg=int(m.group(2))) or f"轉頭 {m.group(2)} 度。",
        ),
    ]

def handle_keyword_command(text: str, deps) -> Optional[str]:
    """
    回傳：
      - None：沒有命中關鍵字，讓文字照常進 LLM 對話
      - str ：命中關鍵字並已執行動作，上層可選擇把這段文字送進 LLM 讓它「說出來」
    """
    t = (text or "").strip()
    if not t:
        return None

    for cmd in build_commands():
        m = cmd.pattern.search(t)
        if m:
            # 執行本地動作
            resp = cmd.handler(deps, m)
            # resp 可以是 None 或 字串
            return resp if isinstance(resp, str) and resp.strip() else ""
    return None

