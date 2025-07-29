import asyncio
import json
import os
import sqlite3
import threading
from datetime import datetime
from typing import Any, Dict

from .constants import LOG_LEVELS
from .utils.colors import Color
from .utils.time import currentDate, currentTime, currentTimeStamp, currentTimeZone


class Tamga:
    """
    A modern logging utility that supports console, file, and JSON logging with colored output.
    """

    LOG_LEVELS = LOG_LEVELS

    __slots__ = [
        "isColored",
        "logToFile",
        "logToJSON",
        "logToConsole",
        "logToMongo",
        "logToSQL",
        "showDay",
        "showTime",
        "showTimezone",
        "mongoURI",
        "mongoDatabaseName",
        "mongoCollectionName",
        "logFile",
        "logJSON",
        "logSQL",
        "sqlTable",
        "notifyServices",
        "notifyLevels",
        "notifyTitle",
        "notifyFormat",
        "maxLogSize",
        "maxJsonSize",
        "maxSqlSize",
        "enableBackup",
        "bufferSize",
        "maxLevelWidth",
        "_mongo_client",
        "_apprise",
        "_notify_executor",
        "_file_buffer",
        "_json_buffer",
        "_buffer_lock",
        "_color_cache",
        "_json_file_handle",
        "_log_file_handle",
    ]

    def __init__(
        self,
        isColored: bool = True,
        logToFile: bool = False,
        logToJSON: bool = False,
        logToConsole: bool = True,
        logToMongo: bool = False,
        logToSQL: bool = False,
        showDay: bool = True,
        showTime: bool = True,
        showTimezone: bool = False,
        mongoURI: str = None,
        mongoDatabaseName: str = "tamga",
        mongoCollectionName: str = "logs",
        logFile: str = "tamga.log",
        logJSON: str = "tamga.json",
        logSQL: str = "tamga.db",
        sqlTable: str = "logs",
        notifyServices: list = None,
        notifyLevels: list = [],
        notifyTitle: str = "{appname}: {level} - {date}",
        notifyFormat: str = "text",
        maxLogSize: int = 10,
        maxJsonSize: int = 10,
        maxSqlSize: int = 50,
        enableBackup: bool = True,
        bufferSize: int = 50,
    ):
        """
        Initialize Tamga with optional features.

        Args:
            isColored: Enable colored console output (default: True)
            logToFile: Enable logging to a file (default: False)
            logToJSON: Enable logging to a JSON file (default: False)
            logToConsole: Enable logging to console (default: True)
            logToMongo: Enable logging to MongoDB (default: False)
            logToSQL: Enable logging to SQL database (default: False)
            showDay: Show day in console logs (default: True)
            showTime: Show time in console logs (default: True)
            showTimezone: Show timezone in console logs (default: False)
            mongoURI: MongoDB connection URI
            mongoDatabaseName: MongoDB database name (default: "tamga")
            mongoCollectionName: MongoDB collection name (default: "logs")
            logFile: Path to the log file (default: "tamga.log")
            logJSON: Path to the JSON log file (default: "tamga.json")
            logSQL: Path to the SQL log file (default: "tamga.db")
            sqlTable: SQL table name for logs (default: "logs")
            notifyServices: List of Apprise notification service URLs
            notifyLevels: List of log levels to send notifications for (default: includes NOTIFY)
            notifyTitle: Template for notification titles (default: "{appname}: {level} - {date}")
            notifyFormat: Notification format type - text/markdown/html (default: "text")
            maxLogSize: Maximum size in MB for log file (default: 10)
            maxJsonSize: Maximum size in MB for JSON file (default: 10)
            maxSqlSize: Maximum size in MB for SQL file (default: 50)
            enableBackup: Enable backup when max size is reached (default: True)
            bufferSize: Number of logs to buffer before writing to file (default: 50)
        """
        self.isColored = isColored
        self.logToFile = logToFile
        self.logToJSON = logToJSON
        self.logToConsole = logToConsole
        self.logToMongo = logToMongo
        self.logToSQL = logToSQL
        self.showDay = showDay
        self.showTime = showTime
        self.showTimezone = showTimezone
        self.mongoURI = mongoURI
        self.mongoDatabaseName = mongoDatabaseName
        self.mongoCollectionName = mongoCollectionName
        self.logFile = logFile
        self.logJSON = logJSON
        self.logSQL = logSQL
        self.sqlTable = sqlTable
        self.notifyServices = notifyServices or []
        self.notifyTitle = notifyTitle
        self.notifyFormat = notifyFormat
        self.notifyLevels = list(set(notifyLevels + ["NOTIFY"]))
        self.maxLogSize = maxLogSize
        self.maxJsonSize = maxJsonSize
        self.maxSqlSize = maxSqlSize
        self.enableBackup = enableBackup
        self.bufferSize = bufferSize
        self.maxLevelWidth = max(len(level) for level in self.LOG_LEVELS)
        self._mongo_client = None
        self._apprise = None
        self._notify_executor = None
        self._file_buffer = []
        self._json_buffer = []
        self._buffer_lock = threading.Lock()
        self._color_cache = {}
        self._json_file_handle = None
        self._log_file_handle = None
        self._init_services()

    def _init_services(self):
        """Initialize external services and create necessary files."""
        if self.logToMongo:
            self._init_mongo()

        if self.logToFile:
            self._ensure_file_exists(self.logFile)
            try:
                self._log_file_handle = open(
                    self.logFile, "a", encoding="utf-8", buffering=8192
                )
            except Exception:
                pass

        if self.logToJSON:
            self._init_json_file()

        if self.logToSQL:
            self._init_sql_db()

    def _init_mongo(self):
        """Initialize MongoDB connection."""
        try:
            import motor.motor_asyncio

            client = motor.motor_asyncio.AsyncIOMotorClient(
                self.mongoURI, tls=True, tlsAllowInvalidCertificates=True
            )
            self._mongo_client = client[self.mongoDatabaseName][
                self.mongoCollectionName
            ]
            self._log_internal("Connected to MongoDB", "TAMGA", "lime")
        except Exception as e:
            self._log_internal(f"Failed to connect to MongoDB: {e}", "CRITICAL", "red")

    def _init_apprise(self):
        """Lazy initialize Apprise for performance."""
        if self._apprise is None and self.notifyServices:
            try:
                import apprise

                self._apprise = apprise.Apprise()

                for service in self.notifyServices:
                    self._apprise.add(service)

                from concurrent.futures import ThreadPoolExecutor

                self._notify_executor = ThreadPoolExecutor(
                    max_workers=2, thread_name_prefix="tamga-notify"
                )

                self._log_internal(
                    f"Notification services initialized: {len(self.notifyServices)} services",
                    "TAMGA",
                    "lime",
                )
            except ImportError:
                self._log_internal(
                    "Apprise not installed. Install with: pip install tamga[notifications]",
                    "WARNING",
                    "amber",
                )
            except Exception as e:
                self._log_internal(
                    f"Failed to initialize notifications: {e}", "ERROR", "red"
                )

    def _send_notification_async(self, message: str, level: str, title: str = None):
        """Send notification asynchronously without blocking."""
        if not self.notifyServices or not self._apprise:
            return

        def send():
            try:
                final_title = title or self.notifyTitle.format(
                    appname="Tamga", level=level, date=currentDate(), time=currentTime()
                )
                formatted_message = self._apply_default_template(message, level)

                self._apprise.notify(
                    body=formatted_message,
                    title=final_title,
                    body_format=self.notifyFormat,
                )
            except Exception as e:
                self._log_internal(f"Notification failed: {e}", "ERROR", "red")

        if self._notify_executor:
            self._notify_executor.submit(send)
        else:
            threading.Thread(target=send, daemon=True).start()

    def _apply_default_template(self, message: str, level: str) -> str:
        """Apply notification templates using the unified apprise module."""
        try:
            from .utils.apprise import format_notification

            return format_notification(
                message, level, currentDate(), currentTime(), self.notifyFormat
            )
        except Exception as e:
            self._log_internal(
                f"Failed to apply notification template: {e}", "ERROR", "red"
            )
            return message

    def _init_json_file(self):
        """Initialize JSON log file."""
        if not os.path.exists(self.logJSON):
            with open(self.logJSON, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _init_sql_db(self):
        """Initialize SQLite database."""
        self._ensure_file_exists(self.logSQL)
        with sqlite3.connect(self.logSQL) as conn:
            conn.execute(
                f"""CREATE TABLE IF NOT EXISTS {self.sqlTable}
                (level TEXT, message TEXT, date TEXT, time TEXT,
                timezone TEXT, timestamp REAL)"""
            )

    def _ensure_file_exists(self, filepath: str):
        """Ensure file exists, create if not."""
        if not os.path.exists(filepath):
            os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
            open(filepath, "w", encoding="utf-8").close()

    def _format_timestamp(self) -> str:
        """Format timestamp string based on settings."""
        parts = []
        if self.showDay:
            parts.append(currentDate())
        if self.showTime:
            parts.append(currentTime())
        if self.showTimezone:
            parts.append(currentTimeZone())
        return " | ".join(parts) if parts else ""

    def _log_internal(self, message: str, level: str, color: str):
        """Internal logging for Tamga messages."""
        if self.logToConsole:
            self._write_to_console(message, level, color)

    def log(self, message: str, level: str, color: str) -> None:
        """
        Main logging method that handles all types of logs.
        """

        log_data = {
            "message": message,
            "level": level,
            "color": color,
            "timestamp": self._format_timestamp(),
            "date": currentDate(),
            "time": currentTime(),
            "timezone": currentTimeZone(),
            "unix_timestamp": currentTimeStamp(),
        }

        if self.logToConsole:
            self._write_to_console(message, level, color)

        if self.logToFile:
            self._buffer_file_write(log_data)

        if self.logToJSON:
            self._buffer_json_write(log_data)

        if self.logToSQL:
            self._write_to_sql(log_data)

        if level in self.notifyLevels and self.notifyServices:
            if self._apprise is None:
                self._init_apprise()

            self._send_notification_async(message, level)

        if self.logToMongo:
            self._write_to_mongo_async(log_data)

    def _buffer_file_write(self, log_data: Dict[str, Any]):
        """Buffer file writes for better performance."""
        with self._buffer_lock:
            self._file_buffer.append(log_data)
            if len(self._file_buffer) >= self.bufferSize:
                self._flush_file_buffer()

    def _buffer_json_write(self, log_data: Dict[str, Any]):
        """Buffer JSON writes for better performance."""
        with self._buffer_lock:
            self._json_buffer.append(log_data)
            if len(self._json_buffer) >= self.bufferSize:
                self._flush_json_buffer()

    def _flush_file_buffer(self):
        """Flush file buffer to disk."""
        if not self._file_buffer:
            return

        self._handle_file_rotation(self.logFile, self.maxLogSize)

        try:
            if self._log_file_handle and not self._log_file_handle.closed:
                for log_data in self._file_buffer:
                    file_timestamp = f"{log_data['date']} | {log_data['time']} | {log_data['timezone']}"
                    self._log_file_handle.write(
                        f"[{file_timestamp}] {log_data['level']}: {log_data['message']}\n"
                    )
                self._log_file_handle.flush()
            else:
                with open(self.logFile, "a", encoding="utf-8") as f:
                    for log_data in self._file_buffer:
                        file_timestamp = f"{log_data['date']} | {log_data['time']} | {log_data['timezone']}"
                        f.write(
                            f"[{file_timestamp}] {log_data['level']}: {log_data['message']}\n"
                        )
            self._file_buffer.clear()
        except Exception as e:
            self._log_internal(f"Failed to write to file: {e}", "ERROR", "red")

    def _flush_json_buffer(self):
        """Flush JSON buffer to disk efficiently."""
        if not self._json_buffer:
            return

        self._handle_file_rotation(self.logJSON, self.maxJsonSize)

        try:
            with open(self.logJSON, "r+", encoding="utf-8") as f:
                f.seek(0, 2)
                file_size = f.tell()

                if file_size > 2:
                    f.seek(file_size - 2)
                    f.write(",\n")
                else:
                    f.seek(0)
                    f.write("[\n")

                entries = [
                    json.dumps(
                        {
                            "level": log["level"],
                            "message": log["message"],
                            "date": log["date"],
                            "time": log["time"],
                            "timezone": log["timezone"],
                            "timestamp": log["unix_timestamp"],
                        },
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )
                    for log in self._json_buffer
                ]

                f.write(",\n".join(entries))
                f.write("\n]")

            self._json_buffer.clear()
        except Exception as e:
            self._log_internal(f"Failed to write to JSON: {e}", "ERROR", "red")

    def _get_color_codes(self, color: str) -> tuple:
        """Get cached color codes for performance."""
        if color not in self._color_cache:
            self._color_cache[color] = (Color.text(color), Color.background(color))
        return self._color_cache[color]

    def _write_to_console(self, message: str, level: str, color: str):
        """Write formatted log entry to console."""
        if not self.isColored:
            timestamp = self._format_timestamp()
            if timestamp:
                print(f"[ {timestamp} ]  {level:<{self.maxLevelWidth}}  {message}")
            else:
                print(f"{level:<{self.maxLevelWidth}}  {message}")
            return

        text_color, bg_color = self._get_color_codes(color)

        output_parts = []

        if self.showDay or self.showTime or self.showTimezone:
            output_parts.append(f"{Color.text('gray')}[{Color.endCode}")

            content_parts = []

            if self.showDay:
                content_parts.append(
                    f"{Color.text('indigo')}{currentDate()}{Color.endCode}"
                )

            if self.showTime:
                content_parts.append(
                    f"{Color.text('violet')}{currentTime()}{Color.endCode}"
                )

            if self.showTimezone:
                content_parts.append(
                    f"{Color.text('purple')}{currentTimeZone()}{Color.endCode}"
                )

            if content_parts:
                separator = f"{Color.text('gray')} | {Color.endCode}"
                output_parts.append(separator.join(content_parts))

            output_parts.append(f"{Color.text('gray')}]{Color.endCode}")

        level_str = (
            f"{bg_color}"
            f"{Color.style('bold')}"
            f" {level:<{self.maxLevelWidth}} "
            f"{Color.endCode}"
        )

        output_parts.append(level_str)
        output_parts.append(f"{text_color}{message}{Color.endCode}")

        print(" ".join(output_parts))

    def _write_to_sql(self, log_data: Dict[str, Any]):
        """Write log entry to SQL database."""
        self._handle_file_rotation(self.logSQL, self.maxSqlSize)

        try:
            with sqlite3.connect(self.logSQL) as conn:
                conn.execute(
                    f"INSERT INTO {self.sqlTable} VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        log_data["level"],
                        log_data["message"],
                        log_data["date"],
                        log_data["time"],
                        log_data["timezone"] or "",
                        log_data["unix_timestamp"],
                    ),
                )
        except Exception as e:
            self._log_internal(f"Failed to write to SQL: {e}", "ERROR", "red")

    def _write_to_mongo_async(self, log_data: Dict[str, Any]):
        """Write to MongoDB asynchronously."""
        if self._mongo_client is None:
            return

        async def write():
            try:
                await self._mongo_client.insert_one(
                    {
                        "level": log_data["level"],
                        "message": log_data["message"],
                        "date": log_data["date"],
                        "time": log_data["time"],
                        "timezone": log_data["timezone"],
                        "timestamp": log_data["unix_timestamp"],
                    }
                )
            except Exception as e:
                self._log_internal(f"Failed to write to MongoDB: {e}", "ERROR", "red")

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(write())
            else:
                loop.run_until_complete(write())
        except RuntimeError:
            asyncio.run(write())

    def _check_file_size(self, filepath: str, max_size_mb: int) -> bool:
        """Check if file size exceeds the maximum size limit."""
        try:
            return os.path.getsize(filepath) >= (max_size_mb * 1024 * 1024)
        except OSError:
            return False

    def _create_backup(self, filepath: str):
        """Create a backup of the file with timestamp."""
        if not os.path.exists(filepath):
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{filepath}.{timestamp}.bak"

        try:
            import shutil

            shutil.copy2(filepath, backup_path)
        except Exception as e:
            self._log_internal(f"Failed to create backup: {e}", "ERROR", "red")

    def _handle_file_rotation(self, filepath: str, max_size_mb: int):
        """Handle file rotation when size limit is reached."""
        if not self._check_file_size(filepath, max_size_mb):
            return

        if filepath == self.logFile and self._log_file_handle:
            self._log_file_handle.close()
            self._log_file_handle = None

        if self.enableBackup:
            self._create_backup(filepath)

        try:
            if filepath.endswith(".json"):
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump([], f)
            elif filepath.endswith(".db"):
                with sqlite3.connect(filepath) as conn:
                    conn.execute(f"DELETE FROM {self.sqlTable}")
            else:
                open(filepath, "w", encoding="utf-8").close()

            if filepath == self.logFile:
                self._log_file_handle = open(
                    self.logFile, "a", encoding="utf-8", buffering=8192
                )
        except Exception as e:
            self._log_internal(f"Failed to rotate file: {e}", "ERROR", "red")

    def flush(self):
        """Flush all buffers to disk."""
        with self._buffer_lock:
            if self._file_buffer:
                self._flush_file_buffer()
            if self._json_buffer:
                self._flush_json_buffer()

    def __del__(self):
        """Cleanup when logger is destroyed."""
        try:
            self.flush()
            if self._notify_executor:
                self._notify_executor.shutdown(wait=False)

            if self._log_file_handle and not self._log_file_handle.closed:
                self._log_file_handle.close()
        except Exception:
            pass

    def info(self, message: str) -> None:
        self.log(message, "INFO", "sky")

    def warning(self, message: str) -> None:
        self.log(message, "WARNING", "amber")

    def error(self, message: str) -> None:
        self.log(message, "ERROR", "rose")

    def success(self, message: str) -> None:
        self.log(message, "SUCCESS", "emerald")

    def debug(self, message: str) -> None:
        self.log(message, "DEBUG", "indigo")

    def critical(self, message: str) -> None:
        self.log(message, "CRITICAL", "red")

    def database(self, message: str) -> None:
        self.log(message, "DATABASE", "green")

    def notify(self, message: str, title: str = None, services: list = None) -> None:
        """
        Send a notification through configured services.

        Args:
            message: Notification message
            title: Optional custom title (overrides template)
            services: Optional list of services (overrides defaults)
        """
        self.log(message, "NOTIFY", "purple")

        if services:
            try:
                import apprise

                temp_apprise = apprise.Apprise()
                for service in services:
                    temp_apprise.add(service)

                final_title = title or self.notifyTitle.format(
                    appname="Tamga",
                    level="NOTIFY",
                    date=currentDate(),
                    time=currentTime(),
                )

                temp_apprise.notify(
                    body=message, title=final_title, body_format=self.notifyFormat
                )
            except Exception as e:
                self._log_internal(f"Custom notification failed: {e}", "ERROR", "red")
        elif self.notifyServices:
            self._send_notification_async(message, "NOTIFY", title)

    def metric(self, message: str) -> None:
        self.log(message, "METRIC", "cyan")

    def trace(self, message: str) -> None:
        self.log(message, "TRACE", "gray")

    def custom(self, message: str, level: str, color: str) -> None:
        self.log(message, level, color)

    def dir(self, message: str, **kwargs) -> None:
        """Log message with additional key-value data."""
        if kwargs:
            data_str = json.dumps(
                kwargs, ensure_ascii=False, separators=(",", ":")
            ).replace('"', "'")
            log_message = f"{message} | {data_str}"
        else:
            log_message = message

        self.log(log_message, "DIR", "yellow")
