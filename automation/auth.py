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
from .exception_context import exception_context
from logger import get_logger

logger = get_logger("automation.auth")


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

    @exception_context("加载Cookie")
    async def load_cookies(self, cookie_file: str = "cookies.json") -> bool:
        """
        从文件加载Cookie到浏览器
        :param cookie_file: Cookie文件路径
        :return: 是否成功加载
        """
        cookie_path = Path(cookie_file)
        if not cookie_path.exists():
            logger.warning(f"⚠ Cookie文件不存在: {cookie_file}")
            return False

        with open(cookie_file, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        await self.context.add_cookies(cookies)
        logger.info(f"✓ Cookie已从文件加载: {cookie_file}")
        return True

    @exception_context("保存Cookie")
    async def save_cookies(self, cookie_file: str = "cookies.json"):
        """
        保存当前浏览器的Cookie到文件
        :param cookie_file: Cookie文件路径
        """
        cookies = await self.context.cookies()
        with open(cookie_file, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Cookie已保存到: {cookie_file}")

    @exception_context("刷新Cookie")
    async def refresh_cookies(self, cookie_file: str = "cookies.json"):
        """
        刷新并保存当前浏览器的Cookie到文件
        :param cookie_file: Cookie文件路径
        """
        refresh_button = self.page.get_by_role('button', name='延长会话')

        # 检查按钮是否存在
        if await refresh_button.count() > 0:
            logger.info("✓ 检测到延长会话按钮，正在点击以刷新Cookie...")
            await refresh_button.click()
            await asyncio.sleep(1)  # 等待cookie更新
            await self.save_cookies(cookie_file)
            await self.load_cookies(cookie_file)

    @exception_context("检查Cookie有效性")
    async def check_cookie_validity(self) -> bool:
        """
        检查Cookie是否有效
        通过检查页面内容是否包含"访客不能访问此课程"来判断
        :return: True表示Cookie有效，False表示Cookie已失效
        """
        page_content = await self.page.content()
        if "访客不能访问此课程" in page_content:
            logger.error("❌ 检测到Cookie已失效")
            return False
        return True

    @exception_context("使用Cookie登录")
    async def login_with_cookies(self, base_url: str, cookie_file: str = "cookies.json") -> bool:
        """
        使用Cookie登录
        :param base_url: 网站首页或任意需要登录的页面URL
        :param cookie_file: Cookie文件路径
        :return: 是否登录成功
        """
        logger.info("正在使用Cookie登录...")

        # 加载Cookie
        if not await self.load_cookies(cookie_file):
            logger.error("\n❌ Cookie加载失败!")
            return False
        # 检查登录状态
        return await self.check_login_status(base_url)

    @exception_context("检查登录状态")
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
        current_parsed = urlparse(current_url)
        base_parsed = urlparse(base_url)

        # Compare scheme, netloc, and path (ignoring query params and fragments)
        if (current_parsed.scheme != base_parsed.scheme or
            current_parsed.netloc != base_parsed.netloc or
            current_parsed.path.rstrip('/') != base_parsed.path.rstrip('/')):
                logger.error(f"❌ Cookie登录失败! 页面被重定向到: {current_url}")
                logger.info("💡 Cookie可能已过期，请重新获取Cookie")
                return False

        logger.info(f"✓ Cookie登录成功,当前页面: {self.page.url}")
        return True

    @exception_context("交互式登录并保存Cookie")
    async def interactive_login_and_save_cookies(self,
                                                 login_url: str,
                                                 base_url: str,
                                                 sso_index_url: str,
                                                 cookie_file: str = "cookies.json") -> bool:
        """
        交互式登录：打开登录页面，等待用户手动登录，然后保存Cookie
        :param login_url: 登录页面URL
        :param base_url: 网站基础URL
        :param cookie_file: Cookie文件路径
        :return: 是否成功登录并保存Cookie
        """
        logger.info("🌐 正在打开登录页面...")
        await self.page.goto(login_url, wait_until='networkidle')
        await self.page.set_viewport_size({"width": 800, "height": 600})
        logger.info(f"✅ 登录页面已打开: {login_url}")
        logger.info("📝 请在浏览器中完成登录操作")
        await asyncio.get_running_loop().run_in_executor(None, input, "🔑 登录完成后，请按回车键继续...")
        # 先前往 SSO 主页
        await self.page.goto(sso_index_url)
        logger.info("🔍 尝试获取cookie...")
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
                logger.info("✅ 成功跳转到目标页面")
        else:
            logger.warning("⚠️ 未找到'砺儒云课堂'链接")
        # 验证Cookie是否有效
        logger.info("🔍 验证登录状态...")
        if await self.check_login_status(base_url):
            logger.info("✅ 登录验证成功！")
        else:
            while not await self.check_login_status(base_url):
                logger.error("❌ 登录验证失败！")
                loop = asyncio.get_running_loop()
                retry = await loop.run_in_executor(None, input, "是否重试？(y/n): ")
                if retry.strip().lower() not in ('y', 'yes'):
                    return False
            logger.info("✅ 登录验证成功！")

        # 保存当前浏览器的Cookie
        await self.save_cookies(cookie_file)
        logger.info(f"✅ Cookie已保存到: {cookie_file}")
        return True
