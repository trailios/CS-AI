from collections    import deque
from threading      import Lock
from datetime       import datetime
from typing         import Dict
from rich.console   import Console
from rich.panel     import Panel
from rich.table     import Table
from rich.text      import Text
from rich.theme     import Theme
from rich.live      import Live
from rich.layout    import Layout

class Logger:
    _lock = Lock()

    LOG_THEME = Theme({
        "info": "cyan",
        "debug": "blue",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
        "log.separator": "dim",
        "log.message": "grey70",
        "log.timestamp": "grey50",
    })

    def __init__(self, live: Live, max_lines_per_panel: int = 10):
        self._live = live
        self.max_lines = max_lines_per_panel
        self._panel_content: Dict[str, deque] = {}
        self._level_order = ["success", "info", "debug", "warning", "error"]
        self._console = Console(theme=self.LOG_THEME)

    def _generate_layout(self) -> Layout:
        layout = Layout()
        
        panel_list = []
        for level in self._level_order:
            if level in self._panel_content:
                level_style = self.LOG_THEME.styles.get(level, "default")
                
                content_table = Table.grid(expand=True)
                for log_entry in self._panel_content[level]:
                    content_table.add_row(log_entry)

                panel = Panel(
                    content_table,
                    title=f" {level.upper()} ",
                    title_align="left",
                    border_style=level_style,
                    padding=(1, 2)
                )
                panel_list.append(panel)
        
        layout.split_column(*panel_list)
        return layout

    def _log(self, level: str, message: str):
        with self._lock:
            if level not in self._panel_content:
                self._panel_content[level] = deque(maxlen=self.max_lines)

            timestamp = datetime.now().strftime("%H:%M:%S")

            log_entry_grid = Table.grid(expand=True)
            log_entry_grid.add_column()
            log_entry_grid.add_column(justify="right")

            separator = Text(" > ", style="log.separator")
            message_text = Text(message, style="log.message")
            main_content = Text.assemble(separator, message_text)
            log_entry_grid.add_row(main_content, Text(timestamp, style="log.timestamp"))

            self._panel_content[level].append(log_entry_grid)
            self._live.update(self._generate_layout(), refresh=True)

    def info(self, message: str):
        self._log("info", message)

    def debug(self, message: str):
        self._log("debug", message)

    def warning(self, message: str):
        self._log("warning", message)

    def error(self, message: str):
        self._log("error", message)

    def success(self, message: str):
        self._log("success", message)


live = Live(
    console=Console(theme=Logger.LOG_THEME),
    screen=True, 
    redirect_stderr=False, 
    renderable=Layout() 
)

logger = Logger(live, max_lines_per_panel=5)