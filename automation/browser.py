"""
浏览器管理模块
负责浏览器的启动、配置和关闭
"""

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from logger import get_logger

logger = get_logger("automation.browser")


class BrowserManager:
    """浏览器管理器"""

    def __init__(self, browser_type: str = "msedge", headless: bool = False):
        """
        初始化浏览器管理器
        :param browser_type: 浏览器类型 (chrome, msedge, firefox)
        :param headless: 是否使用无头模式
        """
        self.browser_type = browser_type
        self.headless = headless
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None

    async def setup(self):
        """启动浏览器并创建页面"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            channel=self.browser_type,
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',  # 防止网站检测自动化
                '--mute-audio'  # 静音浏览器
            ]
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = await self.context.new_page()
        logger.info("✓ 浏览器启动成功 (已静音)")

    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            logger.info("\n✓ 浏览器已关闭")

    def get_page(self) -> Page:
        """获取当前页面对象"""
        return self.page

    def get_context(self) -> BrowserContext:
        """获取浏览器上下文"""
        return self.context
