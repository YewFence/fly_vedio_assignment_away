"""
认证模块
负责Cookie管理和登录验证
"""

import json
import asyncio
from pathlib import Path
from typing import Optional
from playwright.async_api import Page, BrowserContext
from urllib.parse import urlparse


class AuthManager:
    """认证管理器"""

    def __init__(self, page: Page, context: BrowserContext):
        """
        初始化认证管理器
        :param page: Playwright页面对象
        :param context: 浏览器上下文
        """
        self.page = page
        self.context = context

    async def load_cookies(self, cookie_file: str = "cookies.json") -> bool:
        """
        从文件加载Cookie到浏览器
        :param cookie_file: Cookie文件路径
        :return: 是否成功加载
        """
        cookie_path = Path(cookie_file)
        if not cookie_path.exists():
            print(f"⚠ Cookie文件不存在: {cookie_file}")
            return False

        try:
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            await self.context.add_cookies(cookies)
            print(f"✓ Cookie已从文件加载: {cookie_file}")
            return True
        except Exception as e:
            print(f"⚠ 加载Cookie失败: {e}")
            return False

    async def save_cookies(self, cookie_file: str = "cookies.json"):
        """
        保存当前浏览器的Cookie到文件
        :param cookie_file: Cookie文件路径
        """
        cookies = await self.context.cookies()
        with open(cookie_file, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        print(f"✓ Cookie已保存到: {cookie_file}")

    async def refresh_cookies(self, cookie_file: str = "cookies.json"):
        """
        刷新并保存当前浏览器的Cookie到文件
        :param cookie_file: Cookie文件路径
        """
        refresh_button = self.page.get_by_role('button', name='延长会话')

        # 检查按钮是否存在
        if await refresh_button.count() > 0:
            print("✓ 检测到延长会话按钮，正在点击以刷新Cookie...")
            await refresh_button.click()
            await asyncio.sleep(1)  # 等待cookie更新
            await self.save_cookies(cookie_file)

    async def check_cookie_validity(self) -> bool:
        """
        检查Cookie是否有效
        通过检查页面内容是否包含"访客不能访问此课程"来判断
        :return: True表示Cookie有效，False表示Cookie已失效
        """
        try:
            page_content = await self.page.content()
            if "访客不能访问此课程" in page_content:
                print("❌ 检测到Cookie已失效！页面显示: 访客不能访问此课程")
                print("💡 请重新导出browser_cookies.json并运行脚本")
                return False
            return True
        except Exception as e:
            print(f"⚠ Cookie有效性检测出错: {e}")
            return True  # 检测失败时默认认为有效，避免误判

    async def login_with_cookies(self, base_url: str, cookie_file: str = "cookies.json") -> bool:
        """
        使用Cookie登录
        :param base_url: 网站首页或任意需要登录的页面URL
        :param cookie_file: Cookie文件路径
        :return: 是否登录成功
        """
        print("正在使用Cookie登录...")

        # 加载Cookie
        if not await self.load_cookies(cookie_file):
            print("\n❌ Cookie加载失败!")
            print("💡 请按以下步骤手动获取Cookie:")
            print("  1. 在浏览器中登录网站")
            print("  2. 按F12打开开发者工具 -> Application -> Cookies")
            print("  3. 复制所有Cookie并保存为 cookies.json")
            print("  4. 或使用浏览器扩展导出Cookie（推荐）")
            print("\n详细说明请查看: how_to_get_cookie.md")
            return False
        # 检查登录状态
        return await self.check_login_status(base_url)

    async def check_login_status(self, base_url: str) -> bool:
        """
        检查登录状态是否有效
        :param base_url: 网站首页或任意需要登录的页面URL
        :return: 是否登录成功
        """
        # 访问页面验证Cookie是否有效
        await self.page.goto(base_url, wait_until='networkidle')
        await asyncio.sleep(2)

        # 检查是否发生重定向（登录失败会被重定向到登录页）
        current_url = self.page.url

        # 判断是否重定向到了不同的页面
        if current_url != base_url:
            print(f"❌ Cookie登录失败! 页面被重定向到: {current_url}")
            print("💡 Cookie可能已过期，请重新获取Cookie")
            return False

        print(f"✓ Cookie登录成功,当前页面: {self.page.url}")
        return True

    async def interactive_login_and_save_cookies(self, login_url: str, base_url: str, cookie_file: str = "cookies.json") -> bool:
        """
        交互式登录：打开登录页面，等待用户手动登录，然后保存Cookie
        :param login_url: 登录页面URL
        :param base_url: 网站基础URL
        :param cookie_file: Cookie文件路径
        :return: 是否成功登录并保存Cookie
        """
        print("🌐 正在打开登录页面...")
        await self.page.goto(login_url, wait_until='networkidle')
        await self.page.set_viewport_size({"width": 800, "height": 600})
        print(f"✅ 登录页面已打开: {login_url}")
        print("📝 请在浏览器中完成登录操作")
        input("🔑 登录完成后，请按回车键继续...")
        print("🔍 尝试获取cookie...")
        try:
            # 查找文本为"砺儒云课堂"的a标签
            li_ru_link = self.page.get_by_text("砺儒云课堂")
            if await li_ru_link.count() > 0:
                # 使用 context.expect_popup() 来捕捉点击后产生的新页面
                async with self.page.expect_popup() as popup_info:
                    await li_ru_link.first.click()

                    # 这里的 moodle_page 就是新打开的那个标签页
                    moodle_page = await popup_info.value

                    # 等待新页面加载完成
                    await moodle_page.wait_for_load_state()
                    print("✅ 成功跳转到目标页面")
            else:
                print("⚠️ 未找到'lry课堂'链接，继续执行后续操作")
        except Exception as e:
            print(f"⚠️ 点击'lry课堂'链接时出错: {e}")
            print("继续执行后续操作...")
        # 验证Cookie是否有效
        print("🔍 验证登录状态...")
        if await self.check_login_status(base_url):
            print("✅ 登录验证成功！")
        else:
            while not await self.check_login_status(base_url):
                print("❌ 登录验证失败！请确认您已完成登录")
                loop = asyncio.get_running_loop()
                retry = await loop.run_in_executor(None, input, "是否重试？(y/n): ")
                if retry.lower() not in ('y', 'yes'):
                    return False
            print("✅ 登录验证成功！")

        # 保存当前浏览器的Cookie
        await self.save_cookies(cookie_file)
        print(f"✅ Cookie已保存到: {cookie_file}")
        return True
