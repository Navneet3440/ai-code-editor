from datetime import datetime, timezone
import logging
import pytz
from typing import Dict

class ISTFormatter(logging.Formatter):
    """Custom formatter that converts timestamps to IST timezone"""
    
    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        ist = pytz.timezone('Asia/Kolkata')
        return dt.astimezone(ist)
    
    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime("%Y-%m-%d %H:%M:%S %z")

def get_logging_config() -> Dict:
    """
    Get logging configuration with IST timezone and refined formatting.
    Uses a custom formatter to ensure all timestamps are in IST.
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "()": ISTFormatter,
                "format": "[{asctime}] [{levelname}] {name}:{funcName}:{lineno} - {message}",
                "datefmt": "%Y-%m-%d %H:%M:%S %z",
                "style": "{",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "detailed",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": "app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "app": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }


logging.config.dictConfig(get_logging_config())
logger = logging.getLogger("app")