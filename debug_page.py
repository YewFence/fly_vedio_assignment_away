"""
页面结构调试工具
用于分析网页结构，找到正确的CSS选择器
"""

import asyncio
from scripts import VideoAutomation


async def debug():
    """调试页面结构"""

    # ============= 配置你的网站URL =============
    PAGE_URL = "https://example.com/videos"  # 改为你的视频列表页面URL
    CONTAINER_SELECTOR = "body"  # 如果有特定的容器，可以改为具体的选择器，如 "#content"
    # ==========================================

    automation = VideoAutomation(headless=False)

    try:
        print("="*70)
        print("页面结构调试工具")
        print("="*70)

        # 启动浏览器
        await automation.setup()

        # 分析页面结构
        await automation.debug_page_structure(PAGE_URL, CONTAINER_SELECTOR)

        print("\n\n按任意键继续，浏览器将保持打开，方便你手动检查...")
        print("你可以：")
        print("  1. 按F12打开开发者工具")
        print("  2. 使用选择器工具(Ctrl+Shift+C)检查元素")
        print("  3. 在Console中测试CSS选择器: document.querySelectorAll('你的选择器')")

        input()

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await automation.close()


if __name__ == "__main__":
    asyncio.run(debug())
