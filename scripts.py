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
        使用Cookie登录(无需用户名密码)
        :param base_url: 网站首页或任意需要登录的页面URL
        :param cookie_file: Cookie文件路径
        :return: 是否登录成功
        """
        print("尝试使用Cookie登录...")

        # 加载Cookie
        if not await self.load_cookies(cookie_file):
            return False

        # 访问页面验证Cookie是否有效
        await self.page.goto(base_url, wait_until='networkidle')
        await asyncio.sleep(2)

        print(f"✓ 使用Cookie登录成功,当前页面: {self.page.url}")
        return True

    async def login(self, login_url: str, username: str, password: str,
                   username_selector: str, password_selector: str,
                   submit_selector: str, save_cookies: bool = True,
                   cookie_file: str = "cookies.json"):
        """
        登录网站(使用用户名密码)
        :param login_url: 登录页面URL
        :param username: 用户名
        :param password: 密码
        :param username_selector: 用户名输入框的CSS选择器
        :param password_selector: 密码输入框的CSS选择器
        :param submit_selector: 提交按钮的CSS选择器
        :param save_cookies: 是否保存Cookie到文件
        :param cookie_file: Cookie保存路径
        """
        print(f"正在访问登录页面: {login_url}")
        await self.page.goto(login_url, wait_until='networkidle')

        # 等待登录表单加载
        await self.page.wait_for_selector(username_selector, timeout=10000)

        # 输入用户名和密码
        await self.page.fill(username_selector, username)
        await self.page.fill(password_selector, password)
        print("✓ 已输入用户名和密码")

        # 点击登录按钮
        await self.page.click(submit_selector)
        print("✓ 已点击登录按钮")

        # 等待登录完成(等待URL变化或特定元素出现)
        await asyncio.sleep(3)
        print(f"✓ 登录成功,当前页面: {self.page.url}")

        # 保存Cookie
        if save_cookies:
            await self.save_cookies(cookie_file)

    async def get_video_links(self, page_url: str, link_selector: str) -> List[str]:
        """
        获取页面上的所有视频链接
        :param page_url: 包含视频链接的页面URL
        :param link_selector: 链接的CSS选择器
        :return: 视频链接列表
        """
        print(f"\n正在访问视频列表页面: {page_url}")
        await self.page.goto(page_url, wait_until='networkidle')

        # 等待链接加载
        await self.page.wait_for_selector(link_selector, timeout=10000)

        # 获取所有链接
        links = await self.page.eval_on_selector_all(
            link_selector,
            "elements => elements.map(e => e.href || e.getAttribute('href'))"
        )

        # 过滤掉空链接
        links = [link for link in links if link]
        print(f"✓ 找到 {len(links)} 个视频链接")

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
                print("⚠ 无法获取视频时长,将使用默认等待时间")
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

        # 如果需要点击播放按钮
        if play_button_selector:
            try:
                await self.page.wait_for_selector(play_button_selector, timeout=5000)
                await self.page.click(play_button_selector)
                print("✓ 已点击播放按钮")
            except:
                print("⚠ 未找到播放按钮,视频可能自动播放")

        # 获取视频时长
        duration = await self.get_video_duration(video_selector)

        if duration:
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
        else:
            # 使用默认等待时间
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
    """主函数 - 在这里配置你的参数"""

    # ============= 配置区域 - 根据实际情况修改 =============

    # Cookie登录配置
    USE_COOKIE_LOGIN = True  # 是否使用Cookie登录(推荐)
    COOKIE_FILE = "cookies.json"  # Cookie文件路径
    BASE_URL = "https://example.com"  # 网站首页URL(用于验证Cookie)

    # 登录配置(仅在Cookie登录失败时使用)
    LOGIN_URL = "https://example.com/login"  # 登录页面URL
    USERNAME = "your_username"  # 你的用户名
    PASSWORD = "your_password"  # 你的密码
    USERNAME_SELECTOR = "#username"  # 用户名输入框选择器
    PASSWORD_SELECTOR = "#password"  # 密码输入框选择器
    SUBMIT_SELECTOR = "button[type='submit']"  # 登录按钮选择器

    # 视频列表配置
    VIDEO_LIST_URL = "https://example.com/videos"  # 视频列表页面URL
    VIDEO_LINK_SELECTOR = "a.video-link"  # 视频链接选择器

    # 视频播放配置
    VIDEO_ELEMENT_SELECTOR = "video"  # 视频元素选择器
    PLAY_BUTTON_SELECTOR = None  # 播放按钮选择器(如果不需要点击则设为None)
    DEFAULT_WAIT_TIME = 60  # 如果无法获取视频时长,默认等待时间(秒)

    # 浏览器配置
    HEADLESS = False  # 是否使用无头模式(True=不显示浏览器窗口)

    # ====================================================

    automation = VideoAutomation(headless=HEADLESS)

    try:
        # 1. 启动浏览器
        await automation.setup()

        # 2. 登录
        login_success = False

        if USE_COOKIE_LOGIN:
            # 优先尝试Cookie登录
            login_success = await automation.login_with_cookies(BASE_URL, COOKIE_FILE)

        if not login_success:
            # Cookie登录失败或未启用,使用账号密码登录
            print("\n使用账号密码登录...")
            await automation.login(
                LOGIN_URL,
                USERNAME,
                PASSWORD,
                USERNAME_SELECTOR,
                PASSWORD_SELECTOR,
                SUBMIT_SELECTOR,
                save_cookies=True,  # 登录成功后保存Cookie
                cookie_file=COOKIE_FILE
            )

        # 3. 获取视频链接
        video_links = await automation.get_video_links(
            VIDEO_LIST_URL,
            VIDEO_LINK_SELECTOR
        )

        # 4. 观看所有视频
        if video_links:
            await automation.watch_videos(
                video_links,
                VIDEO_ELEMENT_SELECTOR,
                PLAY_BUTTON_SELECTOR,
                DEFAULT_WAIT_TIME
            )
        else:
            print("⚠ 没有找到视频链接")

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 5. 关闭浏览器
        await automation.close()


if __name__ == "__main__":
    asyncio.run(main())
