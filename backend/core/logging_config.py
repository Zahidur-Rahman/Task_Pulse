import logging
import logging.handlers
import os
from pathlib import Path
from core.config import settings

# Create logs directory if it doesn't exist
logs_dir = Path(__file__).parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Log file paths
app_log_file = logs_dir / "app.log"
error_log_file = logs_dir / "error.log"
access_log_file = logs_dir / "access.log"

# Logging format
log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Error log format (more detailed)
error_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def setup_logging():
    """Setup comprehensive logging configuration."""
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler (INFO level and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # Application log file handler (INFO level and above)
    app_handler = logging.handlers.RotatingFileHandler(
        app_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(log_format)
    root_logger.addHandler(app_handler)
    
    # Error log file handler (ERROR level and above)
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(error_format)
    root_logger.addHandler(error_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    
    # Development mode - more verbose logging
    if os.getenv("ENVIRONMENT", "development") == "development":
        root_logger.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)
        app_handler.setLevel(logging.DEBUG)
    
    logging.info("Logging configuration initialized")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)


# Logging utilities
class RequestLogger:
    """Utility class for logging HTTP requests."""
    
    def __init__(self, logger_name: str = "request"):
        self.logger = get_logger(logger_name)
    
    def log_request(self, method: str, url: str, client_ip: str, user_agent: str = None):
        """Log an incoming request."""
        self.logger.info(
            f"Request: {method} {url} - IP: {client_ip}"
            + (f" - UA: {user_agent}" if user_agent else "")
        )
    
    def log_response(self, method: str, url: str, status_code: int, process_time: float):
        """Log a response."""
        self.logger.info(
            f"Response: {method} {url} - Status: {status_code} - Time: {process_time:.4f}s"
        )
    
    def log_error(self, method: str, url: str, error: str, client_ip: str = None):
        """Log an error."""
        self.logger.error(
            f"Error: {method} {url} - {error}"
            + (f" - IP: {client_ip}" if client_ip else "")
        )


class DatabaseLogger:
    """Utility class for logging database operations."""
    
    def __init__(self, logger_name: str = "database"):
        self.logger = get_logger(logger_name)
    
    def log_query(self, query: str, params: dict = None):
        """Log a database query."""
        self.logger.debug(f"Query: {query}" + (f" - Params: {params}" if params else ""))
    
    def log_operation(self, operation: str, table: str, record_id: int = None):
        """Log a database operation."""
        msg = f"DB {operation} on {table}"
        if record_id:
            msg += f" (ID: {record_id})"
        self.logger.info(msg)
    
    def log_error(self, operation: str, error: str, table: str = None):
        """Log a database error."""
        msg = f"DB {operation} error"
        if table:
            msg += f" on {table}"
        msg += f": {error}"
        self.logger.error(msg)


# Initialize logging when module is imported
setup_logging() 