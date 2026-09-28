"""
浏览器管理模块
负责浏览器的启动、配置和关闭
"""

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from ..logger import get_logger

logger = get_logger("automation.browser")


class BrowserManager:
    """浏览器管理器"""

    def __init__(
        self,
        browser_type: str = "msedge",
        headless: bool = False,
        cdp_endpoint: str | None = None,
    ):
        """
        初始化浏览器管理器
        :param browser_type: 浏览器类型 (chrome, msedge)
        :param headless: 是否使用无头模式
        :param cdp_endpoint: 已运行浏览器的 CDP 地址，设置后改为连接该浏览器而不是自行启动
        """
        self.browser_type = browser_type
        self.headless = headless
        self.cdp_endpoint = cdp_endpoint
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    async def setup(self):
        """启动或连接浏览器并创建页面"""
        self.playwright = await async_playwright().start()
        if self.cdp_endpoint:
            self.browser = await self.playwright.chromium.connect_over_cdp(
                self.cdp_endpoint
            )
        else:
            self.browser = await self.playwright.chromium.launch(
                channel=self.browser_type,
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",  # 防止网站检测自动化
                    "--mute-audio",  # 静音浏览器
                ],
            )
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        self.page = await self.context.new_page()
        if self.cdp_endpoint:
            logger.info(f"✓ 已连接到浏览器 {self.cdp_endpoint}")
        else:
            logger.info("✓ 浏览器启动成功 (已静音)")

    async def close(self):
        """关闭浏览器及 Playwright 资源，允许重复调用，清理失败不会抛出异常"""
        had_resources = any(
            resource is not None
            for resource in (self.context, self.browser, self.playwright)
        )

        if self.context is not None:
            try:
                await self.context.close()
            except Exception:
                logger.debug("关闭浏览器上下文时出现异常，忽略", exc_info=True)
            finally:
                self.context = None
                self.page = None

        if self.browser is not None:
            try:
                if self.browser.is_connected():
                    await self.browser.close()
            except Exception:
                logger.debug("关闭浏览器进程时出现异常，忽略", exc_info=True)
            finally:
                self.browser = None

        if self.playwright is not None:
            try:
                await self.playwright.stop()
            except Exception:
                logger.debug("停止 Playwright 时出现异常，忽略", exc_info=True)
            finally:
                self.playwright = None

        if had_resources:
            # CDP 模式下 browser.close() 只断开连接，不会关闭用户自己启动的浏览器
            if self.cdp_endpoint:
                logger.info("\n✓ 已断开与浏览器的连接")
            else:
                logger.info("\n✓ 浏览器已关闭")

    def get_page(self) -> Page:
        """获取当前页面对象"""
        assert self.page is not None
        return self.page

    def get_context(self) -> BrowserContext:
        """获取浏览器上下文"""
        assert self.context is not None
        return self.context
