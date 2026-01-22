import logging
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler

_initialized = False

# 需要压制的第三方库（它们的 DEBUG 日志太吵了）
NOISY_LOGGERS = [
    "playwright",
    "httpx",
    "httpcore",
    "urllib3",
    "asyncio",
]


def setup_logging(
    log_file: str = "debug.log",
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
) -> logging.Logger:
    """
    初始化日志系统
    - 文件处理器：使用 RotatingFileHandler 自动轮转，记录所有级别日志
    - 终端处理器：使用 RichHandler 美化 INFO 及以上级别的输出

    :param log_file: 日志文件路径
    :param max_bytes: 单个日志文件最大字节数，默认 5MB
    :param backup_count: 保留的备份文件数量，默认 3 个
    """
    global _initialized
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # 避免重复添加处理器
    if _initialized:
        return logger

    # --- 1. 文件处理器：自动轮转，记录一切 ---
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    file_handler.setFormatter(file_fmt)

    # --- 2. 终端处理器：追求极致美观 ---
    rich_handler = RichHandler(
        show_time=False,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
    )
    rich_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(rich_handler)

    # --- 3. 压制第三方库的噪音日志 ---
    for name in NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)

    _initialized = True
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    获取指定名称的 logger，自动确保日志系统已初始化
    :param name: logger 名称，通常使用 __name__
    :return: logger 实例
    """
    setup_logging()
    return logging.getLogger(name)
