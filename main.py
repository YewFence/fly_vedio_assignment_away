"""
主入口文件 - 使用模块化架构
配置请在 config.py 中修改
"""

import asyncio
from cookie_fix import cookie_fix
from automation import BrowserManager, AuthManager, VideoManager

# 导入配置
try:
    import config
except ImportError:
    print("❌ 错误: 找不到 config.py 文件!")
    print("请确保 config.py 文件存在于当前目录")
    print("你可以从 config_example.py 复制一份并重命名为 config.py")
    exit(1)


async def main():
    """主函数"""


    # 从 config.py 读取配置
    print("正在加载配置...")

    # 初始化浏览器管理器
    browser_manager = BrowserManager(
        browser_type=config.BROWSER,
        headless=config.HEADLESS
    )

    try:
        # 1. 启动浏览器
        await browser_manager.setup()
        # 2. 初始化认证和视频管理器
        page = browser_manager.get_page()
        context = browser_manager.get_context()

        auth_manager = AuthManager(page, context)
        video_manager = VideoManager(page, auth_manager)

        # 3. 选择登录方式
        print("\n🔐 请选择登录方式:")
        print("   1. 交互式登录（推荐）- 自动打开登录页面，您手动登录后程序自动获取Cookie")
        print("   2. Cookie文件登录 - 使用现有的cookies.json文件登录")
        print("💡 提示：按 Ctrl+C 可随时结束程序")
        
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
                        config.COOKIE_FILE
                    )
                    break
                elif choice == "2":
                    # 使用旧的cookie文件登录方式
                    if cookie_fix():
                        print("✓ Cookie文件格式化成功")
                        login_success = await auth_manager.login_with_cookies(
                            config.BASE_URL,
                            config.COOKIE_FILE
                        )
                    else:
                        print("⚠ Cookie文件格式化失败，请检查browser_cookies.json是否配置正确，程序即将结束")
                    break
                else:
                    print("⚠️  输入无效，请输入 1 或 2，或按 Ctrl+C 结束程序")
            except KeyboardInterrupt:
                print("\n\n程序已由用户中断。")
                return

        if not login_success:
            print("\n❌ 登录失败! 请确保已正确配置 cookies.json 文件或完成手动登录")
            print("详细说明请查看: how_to_get_cookie.md")
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
            print("⚠ 没有找到视频链接")
            print("\n💡 故障排查建议:")
            print("  1. 检查 config.py 中是否正确配置了课程链接")
            print("  2. 确认 cookies.json 文件存在")
            print("  3. 确认 Cookie 是否有效")
            print("  4. 确认网络状态良好")

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

        print("\n💡 故障排查建议:")
        print("  1. 检查 config.py 中是否正确配置了课程链接")
        print("  2. 确认 cookies.json 文件存在")
        print("  3. 确认 Cookie 是否有效")
        print("  4. 确认网络状态良好")
    finally:
        # 6. 关闭浏览器
        input("\n按回车键退出并关闭浏览器...")
        await browser_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
