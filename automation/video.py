"""
视频操作模块
负责视频链接获取、播放控制和时长管理
"""

import asyncio
from typing import List, Optional
from playwright.async_api import Page


class VideoManager:
    """视频管理器"""

    def __init__(self, page: Page, auth_manager):
        """
        初始化视频管理器
        :param page: Playwright页面对象
        :param auth_manager: 认证管理器实例
        """
        self.page = page
        self.auth_manager = auth_manager

    async def get_video_links_by_pattern(self, page_url: str, url_pattern: str) -> List[str]:
        """
        通过URL模式匹配获取视频链接
        :param page_url: 包含视频链接的页面URL
        :param url_pattern: 视频链接的URL模式（如 "https://example.com/mod/fsresource/view.php?id="）
        :return: 视频链接列表
        """
        print(f"\n正在访问视频列表页面: {page_url}")
        await self.page.goto(page_url, wait_until='networkidle')

        # 等待页面加载完成
        await asyncio.sleep(2)

        # 获取所有链接
        links = await self.page.locator(f'a[href*="{url_pattern}"]').evaluate_all(
            'elements => elements.map(e => e.href)'
        )
        # 去重并排序
        links = sorted(list(set(links)))

        print(f"✓ 找到 {len(links)} 个匹配的视频链接")

        # 打印前5个链接作为示例
        if links:
            print("\n示例链接:")
            for i, link in enumerate(links[:5], 1):
                print(f"  {i}. {link}")
            if len(links) > 5:
                print(f"  ... 还有 {len(links) - 5} 个链接")
        else:
            print(f"\n⚠ 未找到匹配模式 '{url_pattern}' 的链接")
            print("💡 提示: 检查 URL_PATTERN 配置是否正确")

        return links

    async def get_video_duration(self, video_selector: str = "video") -> Optional[float]:
        """
        获取视频时长(秒)
        :param video_selector: 视频元素的CSS选择器
        :return: 视频时长(秒),如果获取失败返回None
        """
        try:
            # 等待视频元素加载
            await self.page.wait_for_selector(video_selector, timeout=10000)

            # 获取视频时长
            duration = await self.page.evaluate(f"""
                () => {{
                    const video = document.querySelector('{video_selector}');
                    if (video && video.duration) {{
                        return video.duration;
                    }}
                    return null;
                }}
            """)

            if duration:
                print(f"✓ 视频时长: {duration:.1f} 秒 ({duration/60:.1f} 分钟)")
                return duration
            else:
                print("⚠ 无法获取视频时长,可能并非视频页，将在默认等待时间后跳转下一链接")
                return None

        except Exception as e:
            print(f"⚠ 获取视频时长失败: {e}")
            return None

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
        print(f"\n{'='*60}")
        print(f"正在访问视频页面: {video_url}")
        await self.page.goto(video_url, wait_until='networkidle')

        # 等待页面加载
        await asyncio.sleep(2)

        # 检查Cookie是否有效
        if not await self.auth_manager.check_cookie_validity():
            print("⚠ Cookie已失效，停止观看视频")
            raise Exception("Cookie已失效，请重新获取Cookie")

        # 检查视频是否已完成
        tips_locator = self.page.locator(".tips-completion")
        if await tips_locator.count() > 0:
            # 获取文字内容
            text = await tips_locator.text_content()
            if text and "已完成" in text.strip():
                print("✓ 该视频已标记为完成,跳过观看")
                return

        # 如果需要点击播放按钮
        if play_button_selector:
            try:
                await self.page.wait_for_selector(play_button_selector, timeout=5000)
                await self.page.click(play_button_selector)
                print("✓ 已点击播放按钮")
            except:
                print("⚠ 未找到播放按钮,可能并非视频页，即将自动跳转下一链接")
                return

        # 智能计算视频剩余时间
        duration = None

        try:
            # 获取视频总时长
            video_duration = await self.get_video_duration(video_selector)

            if video_duration is None:
                print("⚠ 无法获取视频总时长")
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
                                print(f"⚠ 已观看时长({watched_duration:.1f}秒) 大于总时长({video_duration:.1f}秒)，视频可能已完成")
                                duration = 0  # 视频已完成，无需等待
                            elif remaining == 0:
                                print("✓ 视频已观看完毕")
                                duration = 0
                            else:
                                duration = remaining
                                print(f"✓ 视频总时长: {video_duration:.1f}秒, 已观看: {watched_duration:.1f}秒, 剩余: {duration:.1f}秒")
                        except ValueError:
                            print(f"⚠ 无法解析已观看时长: '{watched_text}', 使用视频总时长")
                            duration = video_duration
                    else:
                        print("⚠ 已观看时长元素为空，使用视频总时长")
                        duration = video_duration
                else:
                    print("⚠ 未找到已观看时长元素，使用视频总时长")
                    duration = video_duration

        except Exception as e:
            print(f"⚠ 计算剩余时间时出错: {e}")
            duration = None

        # 根据计算结果等待
        if duration is not None and duration > 0:
            # 等待视频播放完成(加上5秒缓冲时间)
            wait_time = duration + 5
            print(f"⏳ 等待视频播放完成(预计 {wait_time:.1f} 秒)...")

            # 分段等待,每10秒显示一次进度
            elapsed = 0
            while elapsed < wait_time:
                chunk = min(10, wait_time - elapsed)
                await asyncio.sleep(chunk)
                elapsed += chunk
                print(f"   已等待 {elapsed:.0f}/{wait_time:.0f} 秒 ({elapsed/wait_time*100:.0f}%)", end='\r', flush=True)
            print()  # 完成后换行
        elif duration == 0:
            # 视频已完成，无需等待
            print("✓ 视频无需等待")
        else:
            # 使用默认等待时间
            print("⚠ 无法获取视频时长，使用默认等待时间...")
            print(f"⏳ 等待 {default_wait_time} 秒...")
            await asyncio.sleep(default_wait_time)

        print("✓ 视频播放完成")

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
        print(f"\n开始观看 {len(video_links)} 个视频")

        for i, link in enumerate(video_links, 1):
            print(f"\n[{i}/{len(video_links)}] 当前视频:")
            await self.play_video(
                link,
                video_selector,
                play_button_selector,
                default_wait_time
            )

            # 视频之间暂停2秒
            if i < len(video_links):
                await asyncio.sleep(2)

        print(f"\n{'='*60}")
        print(f"✓ 所有视频观看完成! 共完成 {len(video_links)} 个视频")
