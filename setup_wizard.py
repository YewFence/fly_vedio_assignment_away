"""
配置引导模块
在程序启动时检测 .env 文件，如果不存在或配置不完整则启动交互式引导
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

console = Console()


def _needs_setup() -> bool:
    """判断是否需要启动配置引导"""
    env_path = Path(".env")

    # 1. .env 文件不存在
    if not env_path.exists():
        return True

    # 2. 加载现有配置检查必填项
    load_dotenv()
    video_url = os.getenv("VIDEO_LIST_URL", "")

    # 3. 必填项缺失或是示例值
    if not video_url or "YOUR_COURSE_ID" in video_url:
        return True

    return False


def _run_wizard() -> dict[str, str]:
    """交互式配置收集"""
    # 欢迎界面
    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]首次运行配置向导[/bold cyan]\n"
            "需要配置课程链接才能使用本工具",
            border_style="cyan",
        )
    )
    console.print()

    # 配置项说明表格
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("配置项", style="cyan", width=20)
    table.add_column("说明", style="white", width=40)
    table.add_column("默认值", style="yellow", width=15)

    table.add_row("BROWSER", "浏览器类型", "msedge")
    table.add_row("HEADLESS", "无头模式（浏览器窗口是否隐藏）", "false")
    table.add_row("VIDEO_LIST_URL", "课程页面链接", "[red]必填[/red]")

    console.print(table)
    console.print()

    # 收集配置 - BROWSER
    browser = Prompt.ask(
        "浏览器类型",
        choices=["msedge", "chrome"],
        default="msedge",
    )

    # 收集配置 - HEADLESS
    headless = Confirm.ask(
        "是否使用无头模式？\n"
        "  [dim]• true: 浏览器窗口不显示（适合挂机）\n"
        "  • false: 浏览器窗口正常显示（推荐新手）[/dim]",
        default=False,
    )

    # 收集配置 - VIDEO_LIST_URL（必填且验证格式）
    console.print()
    while True:
        video_url = Prompt.ask(
            "[bold]课程页面链接[/bold]\n"
            "  [dim]示例: https://moodle.scnu.edu.cn/course/view.php?id=12345[/dim]"
        )

        if not video_url:
            console.print("[red]✗ 链接不能为空[/red]")
            continue

        if "YOUR_COURSE_ID" in video_url:
            console.print("[red]✗ 请替换示例中的 YOUR_COURSE_ID 为实际的课程 ID[/red]")
            continue

        if not video_url.startswith("https://moodle.scnu.edu.cn/course/view.php?id="):
            console.print("[yellow]⚠ 链接格式可能不正确，是否继续？[/yellow]")
            if not Confirm.ask("确认使用此链接", default=False):
                continue

        break

    return {
        "BROWSER": browser,
        "HEADLESS": "true" if headless else "false",
        "VIDEO_LIST_URL": video_url,
    }


def _write_env(config: dict[str, str]) -> None:
    """写入 .env 文件（自动处理扩展名问题）"""
    env_path = Path(".env")

    # 生成内容（保留注释）
    content = f"""# 浏览器类型 (msedge/chrome)
BROWSER={config['BROWSER']}

# 是否使用无头模式 (true/false)
# 若设置为 true，浏览器窗口不会出现，适合想要无感挂机的用户
# 若设置为 false，浏览器窗口会正常出现，适合想要自行确认进度的用户
# 请注意不要手动关闭浏览器 / 杀掉进程，否则程序会直接终止
HEADLESS={config['HEADLESS']}

# 课程链接页面URL
VIDEO_LIST_URL={config['VIDEO_LIST_URL']}
"""

    # 直接写入（Python 会自动创建正确扩展名）
    try:
        env_path.write_text(content, encoding="utf-8")
        console.print(f"[green]✓ 配置已保存到 {env_path.absolute()}[/green]")
    except PermissionError:
        console.print("[red]✗ 无法写入配置文件，请检查目录权限[/red]")
        sys.exit(1)

    # 检测并提示删除 .env.txt
    env_txt = Path(".env.txt")
    if env_txt.exists():
        console.print(
            "[yellow]⚠ 检测到 .env.txt 文件，建议删除（已自动创建正确的 .env）[/yellow]"
        )


def ensure_env_configured() -> None:
    """确保 .env 已正确配置（阻塞式）"""
    if not _needs_setup():
        return  # 配置已存在且有效

    console.print("\n[yellow]⚠ 检测到配置缺失，启动配置向导...[/yellow]\n")

    try:
        config = _run_wizard()
        _write_env(config)
        console.print("\n[bold green]✓ 配置完成！程序即将启动...[/bold green]\n")
    except KeyboardInterrupt:
        console.print("\n[red]✗ 配置已取消，程序退出[/red]")
        sys.exit(0)

