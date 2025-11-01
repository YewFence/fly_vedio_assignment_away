"""
自动视频观看脚本
使用 Playwright 自动登录网站、点击链接并等待视频播放完成
"""

import asyncio
import time
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError
from typing import List, Optional
import re
import json
from pathlib import Path

# 导入配置
try:
    import config
except ImportError:
    print("❌ 错误: 找不到 config.py 文件!")
    print("请确保 config.py 文件存在于当前目录")
    print("你可以从 config_example.py 复制一份并重命名为 config.py")
    exit(1)


class VideoAutomation:
    """视频自动化观看类"""

    def __init__(self, headless: bool = False):
        """
        初始化
        :param headless: 是否使用无头模式(不显示浏览器窗口)
        """
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None

    async def setup(self):
        """启动浏览器"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            channel="msedge",
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']  # 防止网站检测自动化
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = await self.context.new_page()
        print("✓ 浏览器启动成功")

    async def save_cookies(self, cookie_file: str = "cookies.json"):
        """
        保存当前浏览器的Cookie到文件
        :param cookie_file: Cookie文件路径
        """
        cookies = await self.context.cookies()
        with open(cookie_file, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        print(f"✓ Cookie已保存到: {cookie_file}")

    async def load_cookies(self, cookie_file: str = "cookies.json"):
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

    async def login_with_cookies(self, base_url: str, cookie_file: str = "cookies.json"):
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
        from urllib.parse import urlparse
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
                print(f"   已等待 {elapsed:.0f}/{wait_time:.0f} 秒 ({elapsed/wait_time*100:.0f}%)")
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

    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            print("\n✓ 浏览器已关闭")


async def main():
    """主函数 - 配置请在 config.py 中修改"""

    # 从 config.py 读取配置
    print("正在加载配置...")

    automation = VideoAutomation(headless=config.HEADLESS)

    try:
        # 1. 启动浏览器
        await automation.setup()

        # 2. 使用Cookie登录
        login_page = await automation.login_with_cookies(
            config.BASE_URL,
            config.COOKIE_FILE
        )

        # 检查登录是否成功
        login_success = await automation.login_with_cookies(login_page, config.COOKIE_FILE)

        if not login_success:
            print("\n❌ 登录失败! 请确保已正确配置 cookies.json 文件")
            print("详细说明请查看: how_to_get_cookie.md")
            return

        # 3. 通过URL模式获取视频链接
        print(f"\n正在提取视频链接...")
        print(f"URL模式: {config.URL_PATTERN}")

        video_links = await automation.get_video_links_by_pattern(
            config.VIDEO_LIST_URL,
            config.URL_PATTERN
        )

        # 4. 观看所有视频
        if video_links:
            await automation.watch_videos(
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
        # 5. 关闭浏览器
        await automation.close()


if __name__ == "__main__":
    asyncio.run(main())
