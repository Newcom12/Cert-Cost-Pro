"""Настройка логирования через loguru."""
import sys
from pathlib import Path

from loguru import logger


def setup_logging(log_level: str = "INFO") -> None:
    """Настраивает loguru: уровень, формат, ротация."""
    Path("logs").mkdir(exist_ok=True)
    logger.remove()
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    )
    logger.add(
        "logs/bot_{time:YYYY-MM-DD}.log",
        level=log_level,
        rotation="00:00",
        retention="7 days",
        encoding="utf-8",
    )
