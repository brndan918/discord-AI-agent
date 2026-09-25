import io
import logging
import os
import queue
import random
import re
import threading
from datetime import datetime

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.traceback import Traceback

import config

# ---------- 高亮規則 ----------
HIGHLIGHT_RULES = {
    # log level
    r"(?i)\bcritical\b": "bold red",
    r"(?i)\berror\b": "red",
    r"(?i)\bwarn(?:ing)?\b": "yellow",
    r"(?i)\binfo\b": "blue",
    r"(?i)\bdebug\b": "green",

    # memory sizes & durations
    r"\b(KB|MB|GB|TB|ms|sec|seconds|min|hr|day|week|month|year)\b": "bold cyan",

    # boolean/null
    r"\btrue\b|\bfalse\b|\bnull\b|\bNone\b": "dark_blue",

    # string literals (雙引號或單引號包圍的內容)
    r"(['\"])(?:(?=(\\?))\2.)*?\1": "green",
}


class RichFormatter(logging.Formatter):
    # 外框與標題的顏色
    BORDER_COLORS = {
        "DEBUG": "green",
        "INFO": "cyan",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold red",  # 依照要求：bold red 而非 bold white on red
    }

    LEVEL_COLOR = BORDER_COLORS.copy()

    def format_renderable(self, record: logging.LogRecord) -> Panel:
        """不再回傳純字串，而是直接回傳 Rich 的 Panel 物件以達成完美框線"""
        # --- 1. 時間與等級 ---
        ct = datetime.fromtimestamp(record.created)
        asctime = ct.strftime("%Y-%m-%d %H:%M:%S")
        msecs = int(record.msecs)
        rel = int(record.relativeCreated)
        
        # 格式：[2026-03-12 22:20:31.123 +[123]ms] 
        time_str = f"[{asctime}.{msecs:03d} +{rel}ms]"
        hour = ct.hour
        time_color = "bright_yellow" if 6 <= hour <= 17 else "grey50"

        lvl_color = self.LEVEL_COLOR.get(record.levelname, "white")
        
        # 這裡組合頂部第一行
        header_text = f"[{time_color}]{time_str}[/{time_color}] | [{lvl_color}]{record.levelname}[/{lvl_color}] |"

        # --- 2. 路徑與函數 ---
        path = getattr(record, "pathname", record.name)
        lineno = getattr(record, "lineno", 0)

        # ---- 路徑顯示優化 ----
        try:
            base_dir = os.path.abspath(config.BASE_DIR)
            abs_path = os.path.abspath(path)

            if abs_path.startswith(base_dir):
                display_path = os.path.relpath(abs_path, base_dir)
            else:
                display_path = abs_path
        except Exception:
            display_path = path

        try:
            vscode_link = f"vscode://file/{path}:{lineno}"
            path_markup = f"[blue][link={vscode_link}]{lineno}[/link][/blue]"
        except Exception:
            path_markup = path

        func_markup = record.funcName
        try:
            raw_func_name = record.funcName
            func_name = raw_func_name.strip("<>")
            func_def_lineno = 1 if raw_func_name == "<module>" else None

            if func_def_lineno is None and os.path.exists(path) and os.path.isfile(path):
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    for i, line in enumerate(fh, start=1):
                        if re.match(rf'^\s*(async\s+def|def|class)\s+{re.escape(func_name)}\b', line):
                            func_def_lineno = i
                            break

            if func_def_lineno:
                func_vscode_link = f"vscode://file/{path}:{func_def_lineno}"
                func_markup = f"[blue][link={func_vscode_link}]{func_name}[/link][/blue]"
            else:
                func_markup = func_name
        except Exception:
            func_markup = record.funcName.strip("<>")

        path_info = f"{display_path}:{path_markup} in <{func_markup}>"

        # --- 3. 處理內文高亮 ---
        lines = record.getMessage().splitlines() or [""]
        highlighted_lines = []
        for line in lines:
            hl_line = Text(line)
            for pattern, color in HIGHLIGHT_RULES.items():
                try:
                    hl_line.highlight_regex(pattern, style=color)
                except Exception:
                    continue
            highlighted_lines.append(hl_line)

        # 組合 Renderable 群組
        renderables = [
            Text.from_markup(header_text),
            Text.from_markup(path_info),
        ]

        for i, line in enumerate(highlighted_lines):
            prefix = "└─ " if i == len(highlighted_lines) - 1 else "├─ "
            renderables.append(Text(prefix) + line)

        content = Group(*renderables)

        # --- 4. 面板樣式與頻道名稱 ---
        channel_color = getattr(record, "channel_color", "white")
        # 依照要求：不要加上 []
        title_markup = f"[{channel_color}]{record.name}[/{channel_color}]"
        border_style = self.BORDER_COLORS.get(record.levelname, "white")

        # 使用 Panel 產出與 traceback 完全相同的框線效果
        return Panel(
            content,
            title=title_markup,
            border_style=border_style,
            expand=True,          # 展開填滿整個 Console 寬度
            box=box.ROUNDED       # ╭ ─ ╮ │ ╰ ─ ╯ 的邊框樣式
        )

    def format(self, record: logging.LogRecord) -> str:
        # Fallback 保留原生介面
        return super().format(record)


class AsyncRichHandler(logging.Handler):
    """
    非阻塞 Rich logging handler，將 log 訊息放入 queue，由單獨 thread 處理輸出
    並且將每一筆 log（含可能的 traceback）寫到檔案：
      config.BASE_DIR/logs/full/<session_ts>/<log_ts>.log
      config.BASE_DIR/logs/<level_folder>/<session_ts>/<log_ts>.log

    level_folder 映射：
      DEBUG  -> debug
      INFO   -> info
      WARNING-> warning
      ERROR  -> error_exc
      CRITICAL-> critical_exc

    注意：為了跨平台檔名安全，時間字串中的 ":" 會被替換為 "-"。
    """
    LEVEL_FOLDER = {
        "DEBUG": "debug",
        "INFO": "info",
        "WARNING": "warning",
        "ERROR": "error_exc",
        "CRITICAL": "critical_exc",
    }

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.queue = queue.Queue()
        self.formatter = RichFormatter()

        # session timestamp（在 import / handler 建立時固定）
        now = datetime.now()
        # 原始格式含冒號，但檔名上不可含冒號 -> 將 ":" 換成 "-"
        self.session_ts_display = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # e.g. 2026-03-16 20:30:50.220
        self.session_ts_safe = self.session_ts_display.replace(":", "-")    # e.g. 2026-03-16 20-30-50.220

        # 建立 base logs 資料夾結構（若不存在）
        try:
            base_logs = os.path.join(os.path.abspath(config.BASE_DIR), "logs")
            os.makedirs(base_logs, exist_ok=True)
            # 建立各等級根資料夾與 full
            for folder in ("full",) + tuple(set(self.LEVEL_FOLDER.values())):
                os.makedirs(os.path.join(base_logs, folder, self.session_ts_safe), exist_ok=True)
        except Exception:
            # 若建立失敗，不該阻斷 logging，僅忽略
            pass

        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.queue.put(record)
        except Exception:
            self.handleError(record)

    def _worker(self):
        while True:
            record = self.queue.get()
            try:
                # 設定 logger channel_color
                logger = logging.getLogger(record.name)
                record.channel_color = getattr(logger, "channel_color", "white")

                # 直接取得 Panel 物件（RichFormatter 提供）
                renderable = self.formatter.format_renderable(record)

                # 列印到主 Console（帶色彩）
                self.console.print(renderable)

                # 若有 traceback 或 stack_info，也在 console 顯示
                if record.exc_info:
                    try:
                        tb = Traceback.from_exception(*record.exc_info, show_locals=False)
                        self.console.print(tb)
                    except Exception:
                        pass
                elif record.stack_info:
                    self.console.print(record.stack_info)

                # ---- 產生純文字版本以寫入檔案（去除顏色、保留排版） ----
                try:
                    capture_io = io.StringIO()  # 使用 StringIO 代替直接輸出
                    capture_console = Console(file=capture_io, width=self.console.width, color_system=None, record=True)
                    
                    # 先輸出 renderable 到 capture_console（不印到螢幕）
                    capture_console.print(renderable)
                    
                    if record.exc_info:
                        import traceback as _tb
                        tb_text = "".join(_tb.format_exception(*record.exc_info))
                        capture_console.print(tb_text)
                    elif record.stack_info:
                        capture_console.print(record.stack_info)

                    plain_text = capture_io.getvalue()  # 從 StringIO 取得純文字
                except Exception:
                    # fallback：使用 record.getMessage() 與簡易 header
                    ct = datetime.fromtimestamp(record.created)
                    time_str = ct.strftime("%Y-%m-%d %H:%M:%S.") + f"{int(record.msecs):03d}"
                    plain_lines = [f"[{time_str}] | {record.levelname} | {record.name}", record.getMessage()]
                    if record.exc_info:
                        import traceback as _tb
                        plain_lines.append("".join(_tb.format_exception(*record.exc_info)))
                    plain_text = "\n".join(plain_lines)

                # ---- 寫入檔案（同時寫入 full ＆ 等級專屬資料夾） ----
                try:
                    base_logs = os.path.join(os.path.abspath(config.BASE_DIR), "logs")
                    ct = datetime.fromtimestamp(record.created)
                    log_ts_display = ct.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    log_ts_safe = log_ts_display.replace(":", "-")
                    filename = f"{log_ts_safe}.log"

                    targets = [os.path.join(base_logs, "full", self.session_ts_safe)]
                    lvl_folder = self.LEVEL_FOLDER.get(record.levelname, "info")
                    targets.append(os.path.join(base_logs, lvl_folder, self.session_ts_safe))

                    for tgt in targets:
                        try:
                            os.makedirs(tgt, exist_ok=True)
                            path = os.path.join(tgt, filename)
                            with open(path, "w", encoding="utf-8", errors="ignore") as fh:
                                fh.write(plain_text)
                        except Exception:
                            continue
                except Exception:
                    pass

            except Exception:
                self.handleError(record)
            finally:
                self.queue.task_done()


class LogManager:
    CHANNEL_COLORS = [
        "bright_blue",
        "bright_magenta",
        "bright_cyan",
        "bright_green",
        "bright_white",
        "blue",
        "magenta",
        "cyan",
        "green",
    ]

    def __init__(self):
        self._loggers = {}

    def add_logg(self, name: str, level=logging.INFO, color: str | None = None):
        if name in self._loggers:
            return getattr(self, name)

        handler = AsyncRichHandler()

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.handlers.clear()
        logger.addHandler(handler)

        # ---------- 顏色處理 ----------
        if color:
            chosen_color = color if isinstance(color, str) and (color.startswith("#") or color.isalpha()) else "white"
        else:
            used_colors = {lg.channel_color for lg in self._loggers.values() if hasattr(lg, "channel_color")}
            available = [c for c in self.CHANNEL_COLORS if c not in used_colors]
            if available:
                chosen_color = random.choice(available)
            else:
                counts = {c: 0 for c in self.CHANNEL_COLORS}
                for lg in self._loggers.values():
                    c = getattr(lg, "channel_color", None)
                    if c in counts:
                        counts[c] += 1
                min_count = min(counts.values())
                least_used = [c for c, v in counts.items() if v == min_count]
                chosen_color = random.choice(least_used)

        logger.channel_color = chosen_color

        setattr(self, name, logger)
        self._loggers[name] = logger
        return logger


# 單例
log = LogManager()

# # --- 除錯：看效果時，請取消註解。 ---

# LOGGER = log.add_logg(name="DcBot_core", level=logging.DEBUG, color="magenta")

# test_log = """
# 1 / MB 'w' 'w
# """

# LOGGER.debug(test_log)
# LOGGER.critical(test_log)

# def foo():
#     LOGGER.debug(test_log)

# foo()

# try:
#     1 / 0
# except Exception:
#     LOGGER.error("An error occurred!", exc_info=True)

# import time
# time.sleep(1) # 等待 logging 輸出完成，避免測試訊息被截斷
