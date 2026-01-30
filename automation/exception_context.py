from functools import wraps
import asyncio


class BrowserClosedError(Exception):
    """用户手动关闭浏览器时抛出的异常"""

    pass


def _is_browser_closed_error(e: BaseException) -> bool:
    """检查是否为浏览器关闭相关的错误"""
    if isinstance(e, BrowserClosedError):
        return True
    # 检查异常链中是否包含浏览器关闭错误
    if e.__cause__ and _is_browser_closed_error(e.__cause__):
        return True
    # 检查错误消息
    # 不依赖 Playwright 的内部异常类型；用消息匹配即可覆盖“目标已关闭”等场景。
    error_msg = (
        (str(e) or "").lower()
        + " "
        + ("".join(map(str, getattr(e, "args", ()))) or "").lower()
    )
    if any(
        keyword in error_msg
        for keyword in [
            "target page, context or browser has been closed",
            "browser has been closed",
        ]
    ):
        return True
    return False


def exception_context(step_name):
    def decorator(func):
        # 检测是否为异步函数
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    # 检查是否为浏览器关闭错误
                    if _is_browser_closed_error(e):
                        raise BrowserClosedError("用户已关闭浏览器") from None
                    # 统一包装异常
                    raise RuntimeError(f"{step_name}时发生异常") from e

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # 检查是否为浏览器关闭错误
                    if _is_browser_closed_error(e):
                        raise BrowserClosedError("用户已关闭浏览器") from None
                    # 统一包装异常
                    raise RuntimeError(f"{step_name}时发生异常") from e

            return sync_wrapper

    return decorator
