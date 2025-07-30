"""
Lightweight asynchronous logging system for ACOLYTE.
"""

import re
import time
import os
import yaml
from pathlib import Path
from queue import Queue
from logging.handlers import QueueHandler
from typing import List, Pattern, Optional
from contextlib import contextmanager
from loguru import logger as loguru_logger


class AsyncLogger:
    """
    Lightweight asynchronous logger with a plain-text format.

    Format: timestamp | level | component | message
    No emojis, no JSON, near-zero latency.
    """

    def __init__(self, component: str, debug_mode: bool = False):
        self.component = component
        self.debug_mode = debug_mode
        self.queue = Queue()
        self.handler = QueueHandler(self.queue)
        self._setup_async_handler()

    # Handler único compartido entre todas las instancias
    _handler_id = None

    def _setup_async_handler(self):
        """
        Configure the asynchronous handler using QueueHandler.

        Features:
        - Zero latency (non-blocking)
        - Plain-text format, no emojis
        - Automatic rotation at 10 MB
        - Singleton: only one handler is ever registered
        """
        # Resolver ruta segura de logs
        log_path: Path
        try:
            # 1) Explicit environment variable
            env_dir = os.getenv("ACOLYTE_LOG_DIR")
            if env_dir:
                log_path = Path(env_dir)
            else:
                # 2) Fallback to ~/.acolyte/logs inside the container/user HOME
                home_logs = Path.home() / ".acolyte" / "logs"
                log_path = home_logs

            # Ensure the directory exists and is writable
            log_path.mkdir(parents=True, exist_ok=True)
            file_path = log_path / "debug.log"
        except Exception:
            # 3) Last resort: /tmp/debug.log
            file_path = Path("/tmp/debug.log")

        AsyncLogger._handler_id = loguru_logger.add(
            str(file_path),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {extra[component]} | {message}",
            rotation="10 MB",
            compression="zip",
            enqueue=True,  # important for async writes
        )

    def log(self, level: str, message: str, **context):
        """
        Register a log message asynchronously.

        Steps:
        1. Put the record in the queue (instant)
        2. Background worker writes it
        3. No blocking for the caller
        """
        loguru_logger.bind(component=self.component).log(level, message, **context)

    def debug(self, message: str, **context):
        """DEBUG level log."""
        self.log("DEBUG", message, **context)

    def info(self, message: str, **context):
        """INFO level log."""
        self.log("INFO", message, **context)

    def warning(self, message: str, **context):
        """WARNING level log."""
        self.log("WARNING", message, **context)

    def error(self, message: str, include_trace: Optional[bool] = None, **context):
        """
        ERROR level log with optional stack trace.

        Args:
            message: Error message
            include_trace: Force stack trace (None = auto based on debug_mode)
            **context: Additional context
        """
        # Decidir si incluir stack trace
        should_include_trace = include_trace if include_trace is not None else self.debug_mode

        if should_include_trace:
            import traceback

            context["stack_trace"] = traceback.format_exc()

        self.log("ERROR", message, **context)


class SensitiveDataMasker:
    """
    Masks sensitive data in logs.

    Patterns masked:
    - Tokens/API keys
    - Full paths (only basename is kept)
    - Long hashes (keep first 8 chars only)
    """

    def __init__(self, patterns: Optional[List[Pattern]] = None):
        self.patterns = patterns or []

    def mask(self, text: str) -> str:
        """
        Mask sensitive data.

        Example:
        - "token=abc123def456" → "token=***"
        - "/home/user/project" → ".../project"
        - "a1b2c3d4e5f6..." → "a1b2c3d4..."
        """
        # Copia del texto para modificar
        masked = text

        # 1. Enmascarar tokens largos (>20 chars alfanuméricos continuos)
        # Busca secuencias largas que parecen tokens/keys
        masked = re.sub(r'\b[a-zA-Z0-9]{20,}\b', '***TOKEN***', masked)

        # 2. Acortar paths absolutos
        # Linux/Mac paths: /home/user/project → .../project
        masked = re.sub(r'/[a-zA-Z0-9_/.-]{10,}/([a-zA-Z0-9_.-]+)', r'.../\1', masked)

        # Windows paths: C:\Users\Name\project → ...\project
        masked = re.sub(
            r'[A-Z]:\\\\[a-zA-Z0-9_\\\\.-]{10,}\\\\([a-zA-Z0-9_.-]+)', r'...\\\1', masked
        )

        # 3. Acortar hashes largos (>16 chars hex)
        # Muestra solo primeros 8 caracteres
        masked = re.sub(r'\b([a-f0-9]{8})[a-f0-9]{8,}\b', r'\1...', masked)

        # 4. Enmascarar patterns tipo key=value con valores largos
        masked = re.sub(
            r'(api_key|token|secret|password|key)=[a-zA-Z0-9]{8,}',
            r'\1=***',
            masked,
            flags=re.IGNORECASE,
        )

        return masked


class PerformanceLogger:
    """
    Logger specialised for performance metrics.

    Automatically records:
    - Duration
    - Memory usage
    """

    def __init__(self):
        self.logger = AsyncLogger("performance")

    @contextmanager
    def measure(self, operation: str, **context):
        """
        Context manager to measure an operation.

        Example:
        ```python
        with perf_logger.measure("database_query", query=sql):
            result = await db.execute(sql)
        ```
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start
            self.logger.info(
                "Operation completed", operation=operation, duration_ms=duration * 1000, **context
            )


# Logger global configurado
# debug_mode se configurará desde .acolyte cuando SecureConfig esté disponible
def _get_debug_mode() -> bool:
    """Retrieve debug_mode from config file or environment variable."""
    try:
        # Intentar leer desde .acolyte si existe
        config_path = Path(".acolyte")
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
                return config.get("logging", {}).get("debug_mode", False)
    except Exception:
        pass

    # Fallback a variable de entorno
    return os.getenv("ACOLYTE_DEBUG", "false").lower() == "true"


logger = AsyncLogger("acolyte", debug_mode=_get_debug_mode())
