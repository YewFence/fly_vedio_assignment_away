"""
视频操作模块
负责视频链接获取、播放控制和时长管理
"""

import asyncio
from typing import List, Optional
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.console import Console
from .exception_context import exception_context, BrowserClosedError
from logger import get_logger

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
    async def ensure_video_playing(self, video_selector: str = "video") -> dict:
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
        if video_state.get('paused') and not video_state.get('ended'):
            logger.warning("⚠️ 检测到视频已暂停，正在自动恢复播放...")
            await video.evaluate("el => el.play()")
            logger.info("✓ 视频已恢复播放")

        return video_state

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
    async def get_video_links_by_pattern(self, page_url: str, url_pattern: str) -> List[str]:
        """
        通过URL模式匹配获取视频链接
        :param page_url: 包含视频链接的页面URL
        :param url_pattern: 视频链接的URL模式（如 "https://example.com/mod/fsresource/view.php?id="）
        :return: 视频链接列表
        """
        logger.info(f"\n正在访问视频列表页面: {page_url}")
        await self.page.goto(page_url, wait_until='networkidle')

        # 等待页面加载完成
        await asyncio.sleep(2)

        # 获取所有链接
        links = await self.page.locator(f'a[href*="{url_pattern}"]').evaluate_all(
            'elements => elements.map(e => e.href)'
        )
        # 去重并排序
        links = sorted(list(set(links)))

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
    async def get_video_duration(self, video_selector: str = "video") -> Optional[float]:
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
                logger.warning("⚠ 无法获取视频时长,可能并非视频页，将在默认等待时间后跳转下一链接")
                return None

        except TimeoutError:
            # 视频元素不存在是预期行为（可能不是视频页）
            logger.warning("⚠ 未找到视频元素,可能并非视频页")
            return None

    @exception_context("播放视频并等待完成")
    async def play_video(self, video_url: str, video_selector: str = "video",
                        play_button_selector: Optional[str] = None,
                        default_wait_time: int = 60):
        """
        播放视频并等待播放完成
        :param video_url: 视频页面URL
        :param video_selector: 视频元素的CSS选择器
        :param play_button_selector: 播放按钮的CSS选择器(如果需要手动点击播放)
        :param default_wait_time: 如果无法获取视频时长,使用的默认等待时间(秒)
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"正在访问视频页面: {video_url}")
        await self.page.goto(video_url, wait_until='networkidle')

        # 等待页面加载
        await asyncio.sleep(2)

        # 检查浏览器是否已关闭
        await self.check_page_closed()

        # 尝试自动延长会话
        await self.auth_manager.refresh_cookies()

        # 检查Cookie是否有效
        if not await self.auth_manager.check_cookie_validity():
            logger.warning("⚠ Cookie已失效，停止观看视频")
            raise Exception("Cookie已失效，请重新获取Cookie")

        # 检查视频是否已完成
        tips_locator = self.page.locator(".tips-completion")
        if await tips_locator.count() > 0:
            # 获取文字内容
            text = await tips_locator.text_content()
            if text and "已完成" in text.strip():
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

        # 智能计算视频剩余时间
        duration = None

        # 获取视频总时长
        video_duration = await self.get_video_duration(video_selector)

        if video_duration is None:
            logger.warning("⚠ 无法获取视频总时长")
        else:
            # 尝试获取已观看时长
            watched_locator = self.page.locator(".num-gksc > span")

            if await watched_locator.count() > 0:
                watched_text = await watched_locator.text_content()

                if watched_text:
                    # 尝试解析已观看时长（去除空格和可能的单位）
                    watched_text = watched_text.strip()
                    try:
                        watched_duration = float(watched_text)

                        # 计算剩余时间
                        remaining = video_duration - watched_duration

                        if remaining < 0:
                            logger.warning(f"⚠ 已观看时长({self.format_time(watched_duration)}) 大于总时长({self.format_time(video_duration)})，视频可能已完成")
                            duration = 0  # 视频已完成，无需等待
                        elif remaining == 0:
                            logger.info("✓ 视频已观看完毕")
                            duration = 0
                        else:
                            duration = remaining
                            logger.info(f"✓ 总时长: {self.format_time(video_duration)}, 已观看: {self.format_time(watched_duration)}, 剩余: {self.format_time(duration)}")
                    except ValueError:
                        # 数据解析失败是预期行为，使用降级方案
                        logger.warning(f"⚠ 无法解析已观看时长: '{watched_text}', 使用视频总时长")
                        duration = video_duration
                else:
                    logger.warning("⚠ 已观看时长元素为空，使用视频总时长")
                    duration = video_duration
            else:
                logger.warning("⚠ 未找到已观看时长元素，使用视频总时长")
                duration = video_duration

        # 根据计算结果等待
        if duration is not None and duration > 0:
            # 等待视频播放完成
            max_wait_time = duration + 60  # 最大等待时间，防止无限循环
            logger.info(f"⏳ 等待视频播放完成(预计 {self.format_time(duration)})...")

            # 使用 rich 进度条显示播放进度
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=40),
                TaskProgressColumn(),
                TextColumn("•"),
                TimeElapsedColumn(),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task("播放中", total=100)

                elapsed = 0
                while elapsed < max_wait_time:
                    await asyncio.sleep(5)  # 每5秒检查一次
                    elapsed += 5

                    # 检查浏览器是否已关闭
                    await self.check_page_closed()

                    # 检查视频状态并恢复播放
                    video_state = await self.ensure_video_playing(video_selector)

                    if video_state:
                        current_time = video_state.get('currentTime', 0)
                        video_duration = video_state.get('duration', 0)
                        ended = video_state.get('ended', False)

                        # 视频已播放完毕
                        if ended or (video_duration > 0 and current_time >= video_duration - 1):
                            progress.update(task, completed=100, description="[green]播放完毕[/green]")
                            break

                        # 更新进度条
                        if video_duration > 0:
                            percent = current_time / video_duration * 100
                            progress.update(
                                task,
                                completed=percent,
                                description=f"[cyan]{self.format_time(current_time)}[/cyan]/[dim]{self.format_time(video_duration)}[/dim]"
                            )
                    else:
                        # 无法获取视频状态时
                        progress.update(task, description=f"[yellow]等待中 {self.format_time(elapsed)}[/yellow]")

                    # 尝试自动延长会话
                    await self.auth_manager.refresh_cookies()

                    # 检查Cookie是否有效
                    if not await self.auth_manager.check_cookie_validity():
                        logger.error("⚠ Cookie已失效，停止观看视频")
                        raise Exception("Cookie已失效，请重新获取Cookie")

            logger.info("✓ 视频播放完毕")
        elif duration == 0:
            # 视频已完成，无需等待
            logger.info("✓ 视频无需等待")
        else:
            # 使用默认等待时间
            logger.warning("⚠ 无法获取视频时长，使用默认等待时间...")
            logger.info(f"⏳ 等待 {self.format_time(default_wait_time)}...")
            await asyncio.sleep(default_wait_time)

        logger.info("✓ 视频播放完成")

    @exception_context("批量观看视频")
    async def watch_videos(self, video_links: List[str],
                          video_selector: str = "video",
                          play_button_selector: Optional[str] = None,
                          default_wait_time: int = 60):
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
                link,
                video_selector,
                play_button_selector,
                default_wait_time
            )

            # 视频之间暂停2秒
            if i < len(video_links):
                await asyncio.sleep(2)

        logger.info(f"\n{'='*60}")
        logger.info(f"✓ 所有视频观看完成! 共完成 {len(video_links)} 个视频")
