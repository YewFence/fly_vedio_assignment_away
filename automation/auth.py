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

        # 访问页面验证Cookie是否有效
        await self.page.goto(base_url, wait_until='networkidle')
        await asyncio.sleep(2)

        # 检查是否发生重定向（登录失败会被重定向到登录页）
        current_url = self.page.url

        # 提取域名和路径进行比较（忽略查询参数的差异）
        base_parsed = urlparse(base_url)
        current_parsed = urlparse(current_url)

        # 判断是否重定向到了不同的页面
        if base_parsed.netloc != current_parsed.netloc or \
           current_parsed.path.startswith('/login') or \
           current_parsed.path.startswith('/auth'):
            print(f"❌ Cookie登录失败! 页面被重定向到: {current_url}")
            print("💡 Cookie可能已过期，请重新获取Cookie")
            return False

        print(f"✓ Cookie登录成功,当前页面: {self.page.url}")
        return True
