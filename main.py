"""
主入口文件 - 使用模块化架构
配置请在 config.py 中修改
"""

import asyncio
import traceback
from pathlib import Path
from cookie_fix import cookie_fix
from automation import BrowserManager, AuthManager, VideoManager
import config


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
    
    # 显示欢迎界面
    print_welcome()
    
    # 从 config.py 读取配置
    print("📦 正在初始化浏览器...")
    browser_manager = None

    try:
        # 1. 启动浏览器
        browser_manager = BrowserManager(
            browser_type=config.BROWSER,
            headless=config.HEADLESS
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
                print(f"📂 检测到已有 Cookie 文件: {config.COOKIE_FILE}，尝试直接使用该文件登录...")
                login_success = await auth_manager.login_with_cookies(
                    config.BASE_URL,
                    config.COOKIE_FILE
                )
        if not login_success:
            print("登录凭证已失效或不存在")
            # 选择登录方式
            print("\n🔐 请选择获取登录凭证（Cookies）的方式:")
            print("   1. 交互式登录（推荐）- 自动打开登录页面，您手动登录后程序自动获取Cookies")
            print("   2. 使用您手动获取的 Cookies 登录 - 在命令行中直接粘贴浏览器导出的 Cookies JSON")
            
            login_success = False
            while True:
                try:
                    loop = asyncio.get_running_loop()
                    choice = await loop.run_in_executor(None, input, "请输入选择 (1/2，默认为1): ")
                    choice = choice.strip()

                    if choice in ("", "1"):
                        # 默认使用交互式登录
                        login_success = await auth_manager.interactive_login_and_save_cookies(
                            config.LOGIN_URL,
                            config.BASE_URL,
                            config.SSO_INDEX_URL,
                            config.COOKIE_FILE
                        )
                        break
                    elif choice == "2":
                        # 使用手动导出的 cookies 登录
                        if cookie_fix():
                            print("✓ Cookies 格式化成功")
                            login_success = await auth_manager.login_with_cookies(
                                config.BASE_URL,
                                config.COOKIE_FILE
                            )
                        else:
                            print("⚠ Cookies 格式化失败，请检查输入的 Cookies 内容是否正确，程序即将结束")
                        break
                    else:
                        print("⚠️  输入无效，请输入 1 或 2")
                except KeyboardInterrupt:
                    print("\n\n程序已由用户中断。")
                    return

        if not login_success:
            print("\n❌ 登录失败!")
            return

        # 4. 通过URL模式获取视频链接
        print(f"\n正在提取视频链接...")
        print(f"URL模式: {config.URL_PATTERN}")

        video_links = await video_manager.get_video_links_by_pattern(
            config.VIDEO_LIST_URL,
            config.URL_PATTERN
        )

        # 5. 观看所有视频
        if video_links:
            await video_manager.watch_videos(
                video_links,
                config.VIDEO_ELEMENT_SELECTOR,
                config.PLAY_BUTTON_SELECTOR,
                config.DEFAULT_WAIT_TIME
            )
        else:
            print("❌ 未找到任何视频链接。")
            suggestions()

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        traceback.print_exc()
        suggestions()
    finally:
        # 6. 关闭浏览器
        if browser_manager:
            try:
                # 检查浏览器是否仍在运行
                browser = browser_manager.browser
                if browser and browser.is_connected():
                    input("\n按回车键退出并关闭浏览器...")
                    await browser_manager.close()
            except Exception:
                # 浏览器已被手动关闭或其他错误，静默处理
                pass

def suggestions():
    print("\n💡 故障排查建议:")
    print("  1. 检查 config.py 中是否正确配置了课程链接")
    print("  2. 确认 cookies.json 文件存在")
    print("  3. 确认 Cookie 是否有效")
    print("  4. 确认网络状态良好")
    print("  5. 如仍有问题，请提交 issue 至 GitHub 仓库：github.com/YewFence/fly_vedio_assignment_away\n")

if __name__ == "__main__":
    asyncio.run(main())
