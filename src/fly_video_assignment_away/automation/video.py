"""
视频操作模块
负责视频链接获取、播放控制和时长管理
"""

import asyncio

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
)

from ..logger import get_logger
from .exception_context import (
    BrowserClosedError,
    exception_context,
    is_browser_closed_error,
)

logger = get_logger("automation.video")
console = Console()


class VideoManager:
    """视频管理器"""

    @staticmethod
    def format_time(seconds: float) -> str:
        """
        将秒数格式化为友好的时分秒格式
        :param seconds: 秒数
        :return: 格式化后的字符串，如 "1:23:45" 或 "12:34"
        """
        seconds = int(seconds)
        if seconds < 0:
            return "0:00"
        minutes, secs = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    def __init__(self, page: Page, auth_manager):
        """
        初始化视频管理器
        :param page: Playwright页面对象
        :param auth_manager: 认证管理器实例
        """
        self.page = page
        self.auth_manager = auth_manager

    @exception_context("确保视频播放")
    async def ensure_video_playing(self, video_selector: str = "video") -> dict | None:
        """
        确保视频正在播放，如果暂停则自动恢复，并返回视频状态
        :param video_selector: 视频元素的CSS选择器
        :return: 包含视频状态的字典 {paused, currentTime, duration, ended}，获取失败返回 None
        """
        video = self.page.locator(video_selector)
        if await video.count() == 0:
            return None

        # 获取视频状态
        video_state = await video.evaluate("""
            el => ({
                paused: el.paused,
                currentTime: el.currentTime,
                duration: el.duration,
                ended: el.ended
            })
        """)

        # 如果视频暂停了（且未播放完毕），自动恢复播放
        if video_state.get("paused") and not video_state.get("ended"):
            logger.warning("⚠️ 检测到视频已暂停，正在自动恢复播放...")
            await video.evaluate("el => el.play()")
            logger.info("✓ 视频已恢复播放")

        return video_state

    @exception_context("通过学习确认")
    async def pass_human_challenge(self):
        """
        检测并通过平台的"学习确认"弹窗（需按住按钮直到进度条满）
        弹窗未通过期间平台不累计观看时长，因此必须先于恢复播放处理
        """
        challenge_mask = self.page.locator('[id^="anti-bot-"]')
        if await challenge_mask.count() == 0:
            return

        logger.info("🔒 检测到学习确认弹窗，正在按住按钮...")
        await challenge_mask.locator('button[id^="ab-btn-"]').hover()
        await self.page.mouse.down()
        try:
            # 所需按住时长由平台随机生成（约 1.2~2.2 秒），通过后弹窗会被移除
            await challenge_mask.wait_for(state="detached", timeout=10000)
            logger.info("✓ 已通过学习确认")
        except PlaywrightTimeoutError:
            logger.warning("⚠️ 学习确认未通过，将在下次检测时重试")
        finally:
            await self.page.mouse.up()

    @exception_context("检查页面状态")
    async def check_page_closed(self):
        """
        检查页面是否已被用户手动关闭
        如果页面已关闭，打印提示信息并抛出异常
        如果页面正常，静默返回
        """
        # 检查页面是否已关闭
        if self.page.is_closed():
            logger.warning("\n⚠️ 检测到页面已被手动关闭")
            logger.info("💡 程序即将退出")
            raise BrowserClosedError("页面已被用户手动关闭")

    @exception_context("获取视频链接")
    async def get_video_links_by_pattern(
        self, page_url: str, url_pattern: str
    ) -> list[str]:
        """
        通过URL模式匹配获取视频链接
        :param page_url: 包含视频链接的页面URL
        :param url_pattern: 视频链接的URL模式（如 "https://example.com/mod/fsresource/view.php?id="）
        :return: 视频链接列表
        """
        logger.info(f"\n正在访问视频列表页面: {page_url}")
        await self.page.goto(page_url, wait_until="networkidle")

        # 等待页面加载完成
        await asyncio.sleep(2)

        # 只在课程活动中查找，排除导航栏等区域中同样匹配模式的链接（如“使用介绍”）
        links = await self.page.locator(
            f'li.activity a[href*="{url_pattern}"]'
        ).evaluate_all("elements => elements.map(e => e.href)")
        # 同一活动包含多个指向自身的链接，按页面顺序去重以保持课程章节顺序
        links = list(dict.fromkeys(links))

        logger.info(f"✓ 找到 {len(links)} 个匹配的视频链接")

        # 打印前5个链接作为示例
        if links:
            logger.info("\n示例链接:")
            for i, link in enumerate(links[:5], 1):
                logger.info(f"  {i}. {link}")
            if len(links) > 5:
                logger.info(f"  ... 还有 {len(links) - 5} 个链接")
        else:
            logger.warning(f"\n⚠ 未找到匹配模式 '{url_pattern}' 的链接")
            logger.info("💡 提示: 检查 URL_PATTERN 配置是否正确")

        return links

    @exception_context("获取视频时长")
    async def get_video_duration(self, video_selector: str = "video") -> float | None:
        """
        获取视频时长(秒)
        :param video_selector: 视频元素的CSS选择器
        :return: 视频时长(秒),如果获取失败返回None
        """
        try:
            video = self.page.locator(video_selector)
            await video.wait_for(timeout=10000)

            # 获取视频时长
            duration = await video.evaluate("el => el.duration || null")

            if duration:
                logger.info(f"✓ 视频时长: {self.format_time(duration)}")
                return duration
            else:
                logger.warning(
                    "⚠ 无法获取视频时长,可能并非视频页，将在默认等待时间后跳转下一链接"
                )
                return None

        except PlaywrightTimeoutError:
            # 视频元素不存在是预期行为（可能不是视频页）
            logger.warning("⚠ 未找到视频元素,可能并非视频页")
            return None

    async def _read_platform_text(self, selector: str) -> str | None:
        """
        读取平台信息区域中的文本
        不同视频页的平台信息可能缺失或结构不同，读取失败时返回 None 而不中断播放流程
        """
        locator = self.page.locator(selector)
        try:
            if await locator.count() == 0:
                return None
            return (await locator.first.text_content(timeout=2000) or "").strip()
        except PlaywrightError as e:
            if is_browser_closed_error(e):
                raise BrowserClosedError("用户已关闭浏览器") from None
            logger.debug(f"读取平台信息 {selector} 失败，忽略", exc_info=True)
            return None

    async def _read_platform_number(self, selector: str) -> float | None:
        """读取平台信息中的数值，兼容带 % 后缀的写法，无法解析时返回 None"""
        text = await self._read_platform_text(selector)
        if not text:
            return None
        try:
            return float(text.removesuffix("%"))
        except ValueError:
            return None

    async def check_video_completed(self) -> bool:
        """
        检查页面上的完成标记，判断视频是否已被平台标记为完成
        :return: 如果视频已完成返回 True，否则（含标记缺失或读取失败）返回 False
        """
        text = await self._read_platform_text(".tips-completion")
        return text is not None and "已完成" in text

    async def get_platform_watched_seconds(self) -> float | None:
        """
        读取平台记录的观看时长（秒）
        平台分批上报观看时长，该值会阶梯式增长，与视频播放位置不同步
        """
        return await self._read_platform_number(".num-gksc > span")

    async def get_platform_progress_percent(self) -> float | None:
        """读取平台显示的播放进度百分比，即平台判定是否完成所依据的进度"""
        return await self._read_platform_number(".num-bfjd > span")

    async def get_platform_required_percent(self) -> float | None:
        """读取平台要求达到的完成进度百分比（如 90）"""
        return await self._read_platform_number(".tips > span:not(.tips-completion)")

    async def update_platform_progress(
        self,
        progress: Progress,
        task: TaskID,
        target_percent: float,
        target_duration: float,
    ) -> None:
        """
        以平台的完成要求为基线更新完成度进度条：达到要求（如 90%）即为 100%
        优先使用平台显示的播放进度，读不到时用观看时长估算，都读不到则保持原状（首次读到前保持隐藏）
        """
        percent = await self.get_platform_progress_percent()
        watched = await self.get_platform_watched_seconds()
        if percent is not None and target_percent > 0:
            completed = percent / target_percent * 100
        elif watched is not None and target_duration > 0:
            completed = watched / target_duration * 100
        else:
            return
        description = "完成度"
        if watched is not None:
            description += f" [magenta]{self.format_time(watched)}[/magenta]/[dim]{self.format_time(target_duration)}[/dim]"
        progress.update(
            task,
            completed=min(completed, 100),
            description=description,
            visible=True,
        )

    @exception_context("播放视频并等待完成")
    async def play_video(
        self,
        video_url: str,
        video_selector: str = "video",
        play_button_selector: str | None = None,
        default_wait_time: int = 60,
    ):
        """
        播放视频并等待播放完成
        :param video_url: 视频页面URL
        :param video_selector: 视频元素的CSS选择器
        :param play_button_selector: 播放按钮的CSS选择器(如果需要手动点击播放)
        :param default_wait_time: 如果无法获取视频时长,使用的默认等待时间(秒)
        """
        logger.info(f"\n{'=' * 60}")
        logger.info(f"正在访问视频页面: {video_url}")
        await self.page.goto(video_url, wait_until="domcontentloaded")

        # 等待页面加载
        await asyncio.sleep(2)

        # 检查浏览器是否已关闭
        await self.check_page_closed()

        # 尝试自动延长会话
        await self.auth_manager.refresh_cookies()

        # 检查Cookie是否有效
        if not await self.auth_manager.check_cookie_validity():
            logger.warning("⚠ Cookie已失效，停止观看视频")
            raise RuntimeError("Cookie已失效，请重新获取Cookie")

        # 检查视频是否已完成
        if await self.check_video_completed():
            logger.info("✓ 该视频已标记为完成,跳过观看")
            return

        # 如果需要点击播放按钮
        if play_button_selector:
            try:
                await self.page.click(play_button_selector, timeout=5000)
                logger.info("✓ 已点击播放按钮")
            except PlaywrightTimeoutError:
                logger.warning("⚠ 未找到播放按钮,可能并非视频页，即将自动跳转下一链接")
                return

        # 获取视频总时长
        video_duration = await self.get_video_duration(video_selector)

        if video_duration is not None:
            # 以下按平台信息估算的时长只用于展示，不参与完成判断：
            # 是否完成只看平台的完成标记，读不到时退回到视频播放到结尾
            required_percent = await self.get_platform_required_percent()
            if required_percent is None:
                logger.warning("⚠ 无法读取平台的完成要求，按完整看完估算")
            target_percent = required_percent or 100.0
            target_duration = video_duration * target_percent / 100

            info = [f"总时长: {self.format_time(video_duration)}"]
            watched_duration = await self.get_platform_watched_seconds()
            if watched_duration is None:
                logger.warning("⚠ 无法读取平台记录的观看时长")
            else:
                info.append(f"已观看: {self.format_time(watched_duration)}")
            remaining = max(target_duration - (watched_duration or 0.0), 0.0)
            info.append(f"剩余: {self.format_time(remaining)}")
            target_text = self.format_time(target_duration)
            if required_percent is not None:
                target_text += f" ({required_percent:g}%)"
            info.append(f"需观看: {target_text}")
            logger.info(f"✓ {', '.join(info)}")

            # 等待上限只是防止卡死的兜底，按完整视频时长加余量，不依赖平台估算；
            # 正常情况下平台标记完成或视频播放到结尾时会提前退出
            max_wait_time = video_duration + 60
            logger.info("⏳ 等待视频播放完成...")

            # 使用 rich 进度条并列显示视频播放进度和平台记录的观看进度
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=40),
                # 进度保留一位小数，以免平台进度（如 17.8%）被四舍五入成整数
                TaskProgressColumn(
                    text_format="[progress.percentage]{task.percentage:>5.1f}%"
                ),
                console=console,
                transient=True,
            ) as progress:
                video_task = progress.add_task("播放进度", total=100)
                # 读到平台进度前隐藏，避免显示一条不会动的空进度条
                platform_task = progress.add_task("完成度", total=100, visible=False)
                await self.update_platform_progress(
                    progress, platform_task, target_percent, target_duration
                )

                elapsed = 0
                while elapsed < max_wait_time:
                    await asyncio.sleep(5)  # 每5秒检查一次
                    elapsed += 5

                    # 检查浏览器是否已关闭
                    await self.check_page_closed()

                    await self.pass_human_challenge()

                    # 检查视频状态并恢复播放
                    video_state = await self.ensure_video_playing(video_selector)

                    await self.update_platform_progress(
                        progress, platform_task, target_percent, target_duration
                    )

                    # 检查平台是否已标记视频完成
                    if await self.check_video_completed():
                        progress.update(
                            platform_task,
                            description="[green]已完成[/green]",
                        )
                        logger.info("✓ 平台已标记视频完成")
                        break

                    if video_state:
                        current_time = video_state.get("currentTime", 0)
                        video_duration = video_state.get("duration", 0)
                        ended = video_state.get("ended", False)

                        # 视频已播放完毕
                        if ended or (
                            video_duration > 0 and current_time >= video_duration - 1
                        ):
                            progress.update(
                                video_task,
                                completed=100,
                                description="[green]播放完毕[/green]",
                            )
                            logger.info("✓ 视频已播放到结尾")
                            break

                        # 更新进度条
                        if video_duration > 0:
                            percent = current_time / video_duration * 100
                            progress.update(
                                video_task,
                                completed=percent,
                                description=f"播放进度 [cyan]{self.format_time(current_time)}[/cyan]/[dim]{self.format_time(video_duration)}[/dim]",
                            )
                    else:
                        # 无法获取视频状态时
                        progress.update(
                            video_task,
                            description=f"[yellow]等待中 {self.format_time(elapsed)}[/yellow]",
                        )

                    # 尝试自动延长会话
                    await self.auth_manager.refresh_cookies()

                    # 检查Cookie是否有效
                    if not await self.auth_manager.check_cookie_validity():
                        logger.error("⚠ Cookie已失效，停止观看视频")
                        raise RuntimeError("Cookie已失效，请重新获取Cookie")
                else:
                    # 超时只是兜底退出，不代表完成
                    logger.warning(
                        f"⚠ 已等待 {self.format_time(elapsed)} 仍未确认完成（平台未标记完成，视频也未播放到结尾），跳到下一个链接"
                    )
        else:
            # 读不到视频时长就无法判断播放结束，只能按默认时间等待，结束后无法确认是否完成
            logger.warning("⚠ 无法获取视频时长，使用默认等待时间...")
            logger.info(f"⏳ 等待 {self.format_time(default_wait_time)}...")
            await asyncio.sleep(default_wait_time)
            logger.warning("⚠ 已等待默认时间，无法确认该链接是否完成")

    @exception_context("批量观看视频")
    async def watch_videos(
        self,
        video_links: list[str],
        video_selector: str = "video",
        play_button_selector: str | None = None,
        default_wait_time: int = 60,
    ):
        """
        批量观看视频
        :param video_links: 视频链接列表
        :param video_selector: 视频元素的CSS选择器
        :param play_button_selector: 播放按钮的CSS选择器
        :param default_wait_time: 默认等待时间(秒)
        """
        logger.info(f"\n开始观看 {len(video_links)} 个视频")

        for i, link in enumerate(video_links, 1):
            # 检查浏览器是否已关闭
            await self.check_page_closed()

            logger.info(f"\n[{i}/{len(video_links)}] 当前视频:")
            await self.play_video(
                link, video_selector, play_button_selector, default_wait_time
            )

            # 视频之间暂停2秒
            if i < len(video_links):
                await asyncio.sleep(2)

        logger.info(f"\n{'=' * 60}")
        logger.info(f"✓ 所有视频观看完成! 共完成 {len(video_links)} 个视频")
