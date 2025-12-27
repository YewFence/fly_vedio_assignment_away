from functools import wraps
import asyncio

def exception_context(step_name):
    def decorator(func):
        # 检测是否为异步函数
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    # 统一包装异常
                    raise RuntimeError(f"{step_name}时发生异常") from e
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # 统一包装异常
                    raise RuntimeError(f"{step_name}时发生异常") from e
            return sync_wrapper
    return decorator
