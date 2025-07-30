import os
from datetime import datetime

from rich.console import Console


class Logger:
    """
    A versatile logging utility that provides console output with color formatting
    and optional file logging capabilities.

    This logger uses Rich for console output with color formatting and can
    simultaneously write logs to files. It supports different log levels
    (INFO, ERROR, WARN, INIT) and can maintain logs in memory for later retrieval.
    """

    def __init__(
        self,
        in_dir: bool = False,
        session: bool = False,
        write_to_file: bool = False,
        prefix: str = "",
    ) -> None:
        """
        Initialize a new Logger instance.

        Creates a logger that can output to console with color formatting and optionally
        write to log files. The logger can be configured to use a dedicated logs directory
        and create session-specific log files.

        Parameters:
            in_dir (bool, optional): If True, logs will be stored in a '/logs' directory.
                                    Defaults to False.
            session (bool, optional): If True, creates a unique log file for each session
                                     with timestamp in the filename. If False, uses a single
                                     'log.txt' file. Defaults to False.
            write_to_file (bool, optional): If True, writes logs to file in addition to
                                           console output. Defaults to False.
            prefix (str, optional): A prefix to add to log messages. Defaults to an empty string.

        Returns:
            None
        """
        self.cls = Console()

        self.write_to_file = write_to_file
        self.prefix = prefix

        self.in_dir = in_dir
        self.path_prefix = ""
        if self.in_dir:
            self.path_prefix = "/logs"
            if not os.path.isdir(f"{os.getcwd()}/logs"):
                if self.write_to_file:
                    os.mkdir(f"{os.getcwd()}/logs")

        self.session = session
        if self.session:
            self.log_file_path = (
                os.getcwd()
                + self.path_prefix
                + "/log_"
                + str(datetime.now()).replace(" ", "_").replace(":", "-")
                + ".txt"
            )
        else:
            self.log_file_path = os.getcwd() + self.path_prefix + "/log.txt"

        self.log_list = []
        self.log_list_to_send = []
        if self.write_to_file:
            log_file = self._open_log_file(mode="w+")
            log_file.write(
                f"-----------------------{self._make_timestamp_string()}-----------------------\n"
            )
            log_file.close()

    def _open_log_file(self, mode: str = "a+"):
        """
        Opens the log file with the specified mode.

        Parameters:
            mode (str, optional): The file opening mode. Defaults to "a+" (append and read).

        Returns:
            file: The opened file object.
        """
        file = open(self.log_file_path, mode, encoding="utf-8")
        return file

    @staticmethod
    def _make_timestamp_string() -> str:
        """
        Creates a formatted timestamp string for log entries.

        Returns:
            str: Current timestamp as a string in the format 'YYYY-MM-DD HH:MM:SS'.
        """
        return str(datetime.now()).split(".")[0]

    def _echo(self, msg: str, m_type: str) -> None:
        """
        Internal method to process and display log messages.

        This method handles both console output with appropriate color formatting
        and file writing if enabled.

        Parameters:
            msg (str): The message content to log.
            m_type (str): The message type/level (INFO, ERROR, WARN, INIT).

        Returns:
            None
        """
        if self.write_to_file:
            prefix_str = f"::{self.prefix} -> " if self.prefix else ""
            bare_log_string = f"[{self._make_timestamp_string()}]{prefix_str}::{m_type}::{msg}\n"

            log_file = self._open_log_file()
            log_file.write(bare_log_string)
            log_file.close()

            self.log_list.append(bare_log_string)
            self.log_list_to_send.append(bare_log_string)

        if m_type == "INFO":
            color_code = "blue bold"
        elif m_type == "ERROR":
            color_code = "red bold"
        elif m_type == "WARN":
            color_code = "yellow bold"
        elif m_type == "INIT":
            color_code = "purple bold"
        else:
            color_code = "white bold"

        prefix_str = f"[red bold]::[/]{self.prefix} -> " if self.prefix else ""
        self.cls.print(
            f"[gray][{self._make_timestamp_string()}][/]{prefix_str}[red bold]::[/][{color_code}]{m_type}[/][red bold]::[/]{msg}"
        )

    def log(self, msg: str):
        """
        Logs an informational message.

        Parameters:
            msg (str): The message to log.

        Returns:
            None
        """
        self._echo(msg, "INFO")

    def error(self, msg: str):
        """
        Logs an error message.

        Parameters:
            msg (str): The error message to log.

        Returns:
            None
        """
        self._echo(msg, "ERROR")

    def warn(self, msg: str):
        """
        Logs a warning message.

        Parameters:
            msg (str): The warning message to log.

        Returns:
            None
        """
        self._echo(msg, "WARN")

    def init(self, msg: str):
        """
        Logs an initialization message.

        Parameters:
            msg (str): The initialization message to log.

        Returns:
            None
        """
        self._echo(msg, "INIT")

    def flush_logs(self, from_start: bool = False) -> list:
        """
        Retrieves and clears the pending log messages.

        Parameters:
            from_start (bool, optional): If True, returns all logs since logger
                                        initialization. If False, returns only logs
                                        since the last flush. Defaults to False.

        Returns:
            list: A list of log message strings.
        """
        if from_start:
            self.log_list_to_send = self.log_list
        log_list = self.log_list_to_send.copy()
        self.log_list_to_send = []
        return log_list
