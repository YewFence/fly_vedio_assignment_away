"""
主入口文件 - 使用模块化架构
配置请在 config.py 中修改
"""

import asyncio
import sys
import warnings
from pathlib import Path
from cookie_fix import cookie_fix
from automation import BrowserManager, AuthManager, VideoManager
from automation.exception_context import BrowserClosedError
from logger import setup_logging, get_logger
import config

# 抑制 asyncio 在 Windows 上关闭时的资源警告
warnings.filterwarnings("ignore", category=ResourceWarning, message=".*unclosed.*")


def _custom_unraisablehook(unraisable):
    """自定义 unraisable 异常处理，抑制浏览器关闭时的 asyncio 清理错误"""
    # 忽略 asyncio transport 相关的清理错误
    if unraisable.exc_type in (ValueError, OSError):
        err_msg = str(unraisable.exc_value).lower()
        if any(
            keyword in err_msg
            for keyword in [
                "i/o operation on closed pipe",
                "closed pipe",
                "unclosed transport",
            ]
        ):
            return  # 静默忽略
    # 其他异常使用默认处理
    sys.__unraisablehook__(unraisable)


def _custom_excepthook(exc_type, exc_value, exc_traceback):
    """全局异常处理器，将未捕获的异常记录到日志文件"""
    # KeyboardInterrupt 不记录日志，只做友好提示
    if issubclass(exc_type, KeyboardInterrupt):
        return
    # 记录完整的异常信息到日志
    logger.critical("未捕获的异常", exc_info=(exc_type, exc_value, exc_traceback))


sys.unraisablehook = _custom_unraisablehook
sys.excepthook = _custom_excepthook

logger = get_logger(__name__)


def print_welcome():
    """打印欢迎界面"""
    welcome_art = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              Fly Vedio Assignment Away                       ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  欢迎使用 FlyVedioAssignmentAway                              ║
║  📖 使用说明: github.com/YewFence/fly_vedio_assignment_away   ║
║  ⚙️  配置文件: config.py                                      ║
║  👤 作者: YewFence                                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(welcome_art)
    print("🚀 程序启动中...\n")
    print("💡 提示: 可按下 Ctrl+C 结束程序\n")


async def main():
    """主函数"""
    # 初始化日志系统
    setup_logging()

    # 显示欢迎界面
    print_welcome()

    # 从 config.py 读取配置
    logger.info("📦 正在初始化浏览器...")
    browser_manager = None

    try:
        # 1. 启动浏览器
        browser_manager = BrowserManager(
            browser_type=config.BROWSER, headless=config.HEADLESS
        )
        await browser_manager.setup()
        # 2. 初始化认证和视频管理器
        page = browser_manager.get_page()
        context = browser_manager.get_context()

        auth_manager = AuthManager(page, context)
        video_manager = VideoManager(page, auth_manager)
        login_success = False
        # 测试模式下跳过尝试，进行登录凭证获取测试
        if not config.TEST_LOGIN_MODE:
            cookie_path = Path(config.COOKIE_FILE)
            # 如果 cookies.json 文件已存在，尝试直接使用已有 Cookies 登录
            if cookie_path.exists():
                logger.info(
                    f"📂 检测到已有 Cookie 文件: {config.COOKIE_FILE}，尝试直接使用该文件登录..."
                )
                login_success = await auth_manager.login_with_cookies(
                    config.BASE_URL, config.COOKIE_FILE
                )
        if not login_success:
            logger.warning("登录凭证已失效或不存在")
            # 选择登录方式 - 保留 print 用于用户交互
            print("\n🔐 请选择获取登录凭证（Cookies）的方式:")
            print(
                "   1. 交互式登录（推荐）- 自动打开登录页面，您手动登录后程序自动获取Cookies"
            )
            print(
                "   2. 使用您手动获取的 Cookies 登录 - 在命令行中直接粘贴浏览器导出的 Cookies JSON"
            )

            login_success = False
            while True:
                try:
                    loop = asyncio.get_running_loop()
                    choice = await loop.run_in_executor(
                        None, input, "请输入选择 (1/2，默认为1): "
                    )
                    choice = choice.strip()

                    if choice in ("", "1"):
                        # 默认使用交互式登录
                        login_success = (
                            await auth_manager.interactive_login_and_save_cookies(
                                config.LOGIN_URL,
                                config.BASE_URL,
                                config.SSO_INDEX_URL,
                                config.COOKIE_FILE,
                            )
                        )
                        break
                    elif choice == "2":
                        # 使用手动导出的 cookies 登录
                        if cookie_fix():
                            logger.info("✓ Cookies 格式化成功")
                            login_success = await auth_manager.login_with_cookies(
                                config.BASE_URL, config.COOKIE_FILE
                            )
                        else:
                            logger.error(
                                "⚠ Cookies 格式化失败，请检查输入的 Cookies 内容是否正确，程序即将结束"
                            )
                        break
                    else:
                        print("⚠️  输入无效，请输入 1 或 2")
                except KeyboardInterrupt:
                    logger.info("\n\n程序已由用户中断。")
                    return

        if not login_success:
            logger.error("\n❌ 登录失败!")
            return

        # 4. 通过URL模式获取视频链接
        logger.info(f"\n正在提取视频链接...")
        logger.info(f"URL模式: {config.URL_PATTERN}")

        video_links = await video_manager.get_video_links_by_pattern(
            config.VIDEO_LIST_URL, config.URL_PATTERN
        )

        # 5. 观看所有视频
        if video_links:
            await video_manager.watch_videos(
                video_links,
                config.VIDEO_ELEMENT_SELECTOR,
                config.PLAY_BUTTON_SELECTOR,
                config.DEFAULT_WAIT_TIME,
            )
        else:
            logger.error("❌ 未找到任何视频链接。")
            suggestions()

    except BrowserClosedError:
        logger.info("\n👋 检测到浏览器已关闭，程序正常退出")
    except Exception:
        # 只打印一次：RichHandler 会负责美化堆栈，避免和 traceback.print_exc() 重复输出。
        logger.error("\n❌ 发生错误", exc_info=True)
        suggestions()


def suggestions():
    logger.info("\n💡 故障排查建议:")
    logger.info("  1. 检查 config.py 中是否正确配置了课程链接")
    logger.info("  2. 确认 cookies.json 文件存在")
    logger.info("  3. 确认 Cookie 是否有效")
    logger.info("  4. 确认网络状态良好")
    logger.info(
        "  5. 如仍有问题，请提交 issue 至 GitHub 仓库：github.com/YewFence/fly_vedio_assignment_away\n"
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已由用户中断，再见！")
