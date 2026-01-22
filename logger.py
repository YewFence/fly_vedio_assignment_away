import logging
from rich.logging import RichHandler


def setup_logging():
    """
    初始化日志系统
    - 文件处理器：记录所有级别日志到 debug.log
    - 终端处理器：使用 RichHandler 美化 INFO 及以上级别的输出
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # --- 1. 文件处理器：记录一切，时间戳最详细 ---
    file_handler = logging.FileHandler("debug.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    file_handler.setFormatter(file_fmt)

    # --- 2. 终端处理器：追求极致美观 ---
    rich_handler = RichHandler(
        show_time=False,
        show_path=False,
        markup=True
    )
    rich_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(rich_handler)

    return logger


def get_logger(name: str = None):
    """
    获取指定名称的 logger
    :param name: logger 名称，通常使用 __name__
    :return: logger 实例
    """
    return logging.getLogger(name)