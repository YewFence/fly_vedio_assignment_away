"""
认证模块
负责Cookie管理和登录验证
"""

import asyncio
import json
from pathlib import Path
from urllib.parse import urlparse

from playwright.async_api import BrowserContext, Page

from logger import get_logger

from .exception_context import exception_context

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

        with open(cookie_file, "r", encoding="utf-8") as f:
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
        with open(cookie_file, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Cookie已保存到: {cookie_file}")

    @exception_context("刷新Cookie")
    async def refresh_cookies(self, cookie_file: str = "cookies.json"):
        """
        刷新并保存当前浏览器的Cookie到文件
        :param cookie_file: Cookie文件路径
        """
        refresh_button = self.page.get_by_role("button", name="延长会话")

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
    async def login_with_cookies(
        self, base_url: str, cookie_file: str = "cookies.json"
    ) -> bool:
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
        await self.page.goto(base_url, wait_until="networkidle")
        await asyncio.sleep(2)

        # 检查是否发生重定向（登录失败会被重定向到登录页）
        current_url = self.page.url

        # 判断是否重定向到了不同的页面
        current_parsed = urlparse(current_url)
        base_parsed = urlparse(base_url)

        # Compare scheme, netloc, and path (ignoring query params and fragments)
        if (
            current_parsed.scheme != base_parsed.scheme
            or current_parsed.netloc != base_parsed.netloc
            or current_parsed.path.rstrip("/") != base_parsed.path.rstrip("/")
        ):
            logger.error(f"❌ Cookie登录失败! 页面被重定向到: {current_url}")
            logger.info("💡 Cookie可能已过期，请重新获取Cookie")
            return False

        logger.info(f"✓ Cookie登录成功,当前页面: {self.page.url}")
        return True

    @exception_context("账号密码登录")
    async def credential_login(
        self,
        username: str,
        password: str,
        login_url: str,
        base_url: str,
        sso_index_url: str,
        cookie_file: str = "cookies.json",
    ) -> bool:
        """
        使用账号密码自动登录SSO并获取Moodle Cookie
        :param username: 登录账号
        :param password: 登录密码
        :param login_url: SSO登录页面URL
        :param base_url: Moodle基础URL
        :param sso_index_url: SSO主页URL
        :param cookie_file: Cookie文件路径
        :return: 是否成功登录
        """
        logger.info("正在打开登录页面...")
        await self.page.goto(login_url, wait_until="networkidle")

        # 填写账号密码（使用 ID 定位，避免 placeholder 重复匹配）
        logger.info("正在填写登录信息...")
        await self.page.locator("#account").fill(username)
        await self.page.locator("#password").fill(password)

        # 点击登录按钮
        logger.info("正在提交登录信息...")
        await self.page.get_by_role("button", name="登录 Sign in").click()

        # 同时等待：页面跳转成功 / 出现错误提示
        nav_task = asyncio.create_task(
            self.page.wait_for_url(
                lambda url: "login.html" not in url, timeout=15000
            )
        )
        error_task = asyncio.create_task(
            self.page.locator("text=用户密码不正确").wait_for(timeout=15000)
        )

        done, pending = await asyncio.wait(
            [nav_task, error_task], return_when=asyncio.FIRST_COMPLETED
        )
        for t in pending:
            t.cancel()

        # 判断结果
        if error_task in done and not error_task.exception():
            logger.error("❌ 登录失败，用户名或密码不正确")
            return False
        if nav_task in done and nav_task.exception():
            logger.error("❌ 登录失败，页面未按预期跳转，请检查账号、密码或网络状态")
            return False

        logger.info("✓ SSO登录成功，正在获取Cookie...")

        # 前往 SSO 主页，点击"砺儒云课堂"获取 Moodle Cookie
        await self.page.goto(sso_index_url, wait_until="networkidle")

        li_ru_link = self.page.get_by_text("砺儒云课堂")
        if await li_ru_link.count() > 0:
            async with self.page.expect_popup() as popup_info:
                await li_ru_link.first.click()
                moodle_page = await popup_info.value
                await moodle_page.wait_for_load_state()
                logger.info("✓ 成功跳转到砺儒云课堂")
                await moodle_page.close()
        else:
            logger.warning("⚠️ 未找到'砺儒云课堂'链接")

        # 验证登录状态并保存Cookie
        logger.info("正在验证登录状态...")
        if await self.check_login_status(base_url):
            await self.save_cookies(cookie_file)
            logger.info("✅ 登录成功，Cookie已保存")
            return True

        logger.error("❌ 登录验证失败")
        return False
