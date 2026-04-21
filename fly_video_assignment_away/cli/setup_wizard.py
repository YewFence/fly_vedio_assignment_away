"""
配置引导模块
在程序启动时检测 .env 文件，如果不存在或配置不完整则启动交互式引导
"""

import os
import re
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

console = Console()
MANAGED_ENV_KEYS = ("BROWSER", "HEADLESS", "VIDEO_LIST_URL")
ENV_ASSIGNMENT_RE = re.compile(
    r"^(\s*(?:export\s+)?)([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)(\s+#.*)?$"
)


def _needs_setup() -> bool:
    """判断是否需要启动配置引导"""
    env_path = Path(".env")

    # 1. 优先检查真实环境变量，避免在 CI / shell 已配置时强制启动向导
    video_url = os.getenv("VIDEO_LIST_URL", "")

    # 2. 若环境变量未提供，再尝试从 .env 加载
    if not video_url and env_path.exists():
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

    try:
        if env_path.exists():
            backup_path = env_path.parent / ".env.bak"
            shutil.copy2(env_path, backup_path)
            console.print(
                f"[yellow]⚠ 已备份现有配置到 {backup_path.absolute()}[/yellow]"
            )
            try:
                existing_content = env_path.read_text(encoding="utf-8")
                content = _merge_env_content(existing_content, config)
            except UnicodeDecodeError:
                console.print(
                    "[yellow]⚠ 现有 .env 不是 UTF-8 编码，将使用新配置重建该文件[/yellow]"
                )
                content = _render_env_content(config)
        else:
            content = _render_env_content(config)

        env_path.write_text(content, encoding="utf-8")
        load_dotenv(env_path, override=True)
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


def _quote_env_value(value: str) -> str:
    """按 .env 语法安全地格式化值"""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _render_env_content(config: dict[str, str]) -> str:
    """生成新的 .env 内容（保留注释）"""
    return f"""# 浏览器类型 (msedge/chrome)
BROWSER={_quote_env_value(config['BROWSER'])}

# 是否使用无头模式 (true/false)
# 若设置为 true，浏览器窗口不会出现，适合想要无感挂机的用户
# 若设置为 false，浏览器窗口会正常出现，适合想要自行确认进度的用户
# 请注意不要手动关闭浏览器 / 杀掉进程，否则程序会直接终止
HEADLESS={_quote_env_value(config['HEADLESS'])}

# 课程链接页面URL
VIDEO_LIST_URL={_quote_env_value(config['VIDEO_LIST_URL'])}
"""


def _merge_env_content(existing_content: str, config: dict[str, str]) -> str:
    """合并现有 .env，保留注释和未知键"""
    updated_keys = set()
    merged_lines = []

    for line in existing_content.splitlines():
        match = ENV_ASSIGNMENT_RE.match(line)
        if not match:
            merged_lines.append(line)
            continue

        prefix, key, _value, comment = match.groups()
        if key not in MANAGED_ENV_KEYS:
            merged_lines.append(line)
            continue

        comment_suffix = comment or ""
        merged_lines.append(
            f"{prefix}{key}={_quote_env_value(config[key])}{comment_suffix}"
        )
        updated_keys.add(key)

    if merged_lines and merged_lines[-1].strip():
        merged_lines.append("")

    for key in MANAGED_ENV_KEYS:
        if key not in updated_keys:
            merged_lines.append(f"{key}={_quote_env_value(config[key])}")

    return "\n".join(merged_lines).rstrip() + "\n"


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
