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
            print("\n详细说明请查看: COOKIE_GUIDE.md")
            return False

        # 访问页面验证Cookie是否有效
        await self.page.goto(base_url, wait_until='networkidle')
        await asyncio.sleep(2)

        print(f"✓ Cookie登录成功,当前页面: {self.page.url}")
        return True

    async def get_video_links(self, page_url: str, link_selector: str) -> List[str]:
        """
        获取页面上的所有视频链接（简单模式）
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

    async def get_nested_video_links(self, page_url: str,
                                    video_li_selector: str,
                                    exclude_class: Optional[str] = None) -> List[str]:
        """
        获取嵌套结构中的视频链接（高级模式）
        适用于: ul > li > ul > li > a 这种嵌套结构

        :param page_url: 包含视频链接的页面URL
        :param video_li_selector: 包含视频链接的li的CSS选择器（要精确到有视频的li）
        :param exclude_class: 需要排除的li的class名称（装饰性元素）
        :return: 视频链接列表
        """
        print(f"\n正在访问视频列表页面: {page_url}")
        await self.page.goto(page_url, wait_until='networkidle')

        # 等待页面加载
        await asyncio.sleep(2)

        # 使用JavaScript提取所有视频链接
        links = await self.page.evaluate(f"""
            () => {{
                const links = [];

                // 找到所有包含视频的li元素
                const videoLis = document.querySelectorAll('{video_li_selector}');

                console.log('找到的li元素数量:', videoLis.length);

                videoLis.forEach((li, index) => {{
                    // 如果指定了排除的class，检查是否需要跳过
                    {f"if (li.classList.contains('{exclude_class}')) {{ return; }}" if exclude_class else "// 不排除任何class"}

                    // 在这个li中查找所有a标签
                    const aElements = li.querySelectorAll('a');

                    aElements.forEach(a => {{
                        const href = a.href || a.getAttribute('href');
                        if (href && href.trim() !== '' && href !== '#') {{
                            // 转换为绝对URL
                            const absoluteUrl = new URL(href, window.location.href).href;
                            links.push(absoluteUrl);
                        }}
                    }});
                }});

                console.log('提取的链接数量:', links.length);
                return links;
            }}
        """)

        # 去重
        links = list(dict.fromkeys(links))

        print(f"✓ 找到 {len(links)} 个视频链接")

        # 打印前5个链接作为示例
        if links:
            print("\n示例链接:")
            for i, link in enumerate(links[:5], 1):
                print(f"  {i}. {link}")
            if len(links) > 5:
                print(f"  ... 还有 {len(links) - 5} 个链接")

        return links

    async def debug_page_structure(self, page_url: str, container_selector: str = "body"):
        """
        调试工具：分析页面结构，帮助找到正确的选择器
        :param page_url: 要分析的页面URL
        :param container_selector: 容器选择器（默认body）
        """
        print(f"\n正在分析页面结构: {page_url}")
        await self.page.goto(page_url, wait_until='networkidle')
        await asyncio.sleep(2)

        structure = await self.page.evaluate(f"""
            () => {{
                const container = document.querySelector('{container_selector}');
                if (!container) return {{ error: '未找到容器元素' }};

                const result = {{
                    uls: [],
                    allLiClasses: new Set(),
                    aTagCount: 0,
                    structure: []
                }};

                // 查找所有ul
                const uls = container.querySelectorAll('ul');

                uls.forEach((ul, ulIndex) => {{
                    const ulInfo = {{
                        index: ulIndex,
                        class: ul.className,
                        id: ul.id,
                        liCount: 0,
                        lis: []
                    }};

                    const lis = ul.querySelectorAll(':scope > li');
                    ulInfo.liCount = lis.length;

                    lis.forEach((li, liIndex) => {{
                        const liClasses = Array.from(li.classList);
                        liClasses.forEach(cls => result.allLiClasses.add(cls));

                        const aElements = li.querySelectorAll('a');
                        const nestedUls = li.querySelectorAll('ul');

                        ulInfo.lis.push({{
                            index: liIndex,
                            classes: liClasses,
                            aCount: aElements.length,
                            nestedUlCount: nestedUls.length,
                            sampleAHref: aElements[0]?.href || null
                        }});

                        result.aTagCount += aElements.length;
                    }});

                    result.uls.push(ulInfo);
                }});

                result.allLiClasses = Array.from(result.allLiClasses);
                return result;
            }}
        """)

        print("\n" + "="*70)
        print("页面结构分析报告")
        print("="*70)

        if "error" in structure:
            print(f"❌ 错误: {structure['error']}")
            return

        print(f"\n📊 统计信息:")
        print(f"  - 找到 {len(structure['uls'])} 个 <ul> 元素")
        print(f"  - 所有 <a> 标签总数: {structure['aTagCount']}")
        print(f"  - 发现的li class类型: {', '.join(structure['allLiClasses']) if structure['allLiClasses'] else '无'}")

        print(f"\n📋 UL详细结构:")
        for ul in structure['uls'][:5]:  # 只显示前5个
            print(f"\n  UL #{ul['index']}:")
            print(f"    - Class: '{ul['class']}'" if ul['class'] else "    - Class: (无)")
            print(f"    - ID: '{ul['id']}'" if ul['id'] else "    - ID: (无)")
            print(f"    - 直接子li数量: {ul['liCount']}")

            for li in ul['lis'][:3]:  # 每个ul只显示前3个li
                print(f"\n      LI #{li['index']}:")
                print(f"        - Classes: {', '.join(li['classes']) if li['classes'] else '(无)'}")
                print(f"        - 包含的<a>数量: {li['aCount']}")
                print(f"        - 嵌套的<ul>数量: {li['nestedUlCount']}")
                if li['sampleAHref']:
                    print(f"        - 示例链接: {li['sampleAHref'][:60]}...")

        print("\n" + "="*70)
        print("\n💡 建议:")
        print("  根据上面的分析，尝试使用以下选择器:")
        print(f"  - 如果视频链接的li有特定class，使用: 'li.{{class_name}}'")
        print(f"  - 如果需要排除装饰性li，使用exclude_class参数")
        print(f"  - 如果是简单的列表，直接使用: 'ul li a'")
        print("="*70)

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
    """主函数 - 配置请在 config.py 中修改"""

    # 从 config.py 读取配置
    print("正在加载配置...")

    automation = VideoAutomation(headless=config.HEADLESS)

    try:
        # 1. 启动浏览器
        await automation.setup()

        # 2. 使用Cookie登录
        login_success = await automation.login_with_cookies(
            config.BASE_URL,
            config.COOKIE_FILE
        )

        if not login_success:
            print("\n❌ 登录失败! 请确保已正确配置 cookies.json 文件")
            print("详细说明请查看: COOKIE_GUIDE.md")
            return

        # 3. 获取视频链接（根据配置的模式选择方法）
        print(f"\n使用 '{config.EXTRACTION_MODE}' 模式提取视频链接...")

        if config.EXTRACTION_MODE == "nested":
            # 嵌套模式：处理复杂的多层列表结构
            video_links = await automation.get_nested_video_links(
                config.VIDEO_LIST_URL,
                config.VIDEO_LI_SELECTOR,
                config.EXCLUDE_CLASS
            )
        else:
            # 简单模式：直接选择所有视频链接
            video_links = await automation.get_video_links(
                config.VIDEO_LIST_URL,
                config.VIDEO_LINK_SELECTOR
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
            print("\n💡 提示:")
            print("  1. 运行 'uv run python debug_page.py' 分析页面结构")
            print("  2. 检查 config.py 中的选择器配置是否正确")
            print("  3. 确认是否需要登录才能看到视频列表")

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

        print("\n💡 故障排查建议:")
        print("  1. 检查 config.py 中的配置是否正确")
        print("  2. 确认 cookies.json 文件存在且有效")
        print("  3. 运行 'uv run python debug_page.py' 分析页面结构")
        print("  4. 确认网站URL是否正确且可访问")
        print("  5. 查看 COOKIE_GUIDE.md 了解如何获取Cookie")

    finally:
        # 5. 关闭浏览器
        await automation.close()


if __name__ == "__main__":
    asyncio.run(main())
