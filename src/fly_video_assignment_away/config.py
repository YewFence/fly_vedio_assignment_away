"""
配置文件
敏感配置从 .env 文件读取，其他配置在此文件中设置
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path.cwd() / ".env")

# ============= 从环境变量读取的配置 =============

# 脚本化运行配置
SKIP_SETUP_WIZARD = os.getenv("SKIP_SETUP_WIZARD", "false").lower() == "true"

# 浏览器配置
BROWSER = os.getenv("BROWSER", "msedge")  # 浏览器类型(msedge/chrome/firefox)
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"  # 是否使用无头模式
# 高级配置：指定浏览器可执行文件（如 Flatpak 导出的启动脚本），设置后忽略 BROWSER
BROWSER_EXECUTABLE_PATH = os.getenv("BROWSER_EXECUTABLE_PATH") or None
# 高级配置：连接已在运行的浏览器，优先级最高，设置后忽略 BROWSER、HEADLESS 和 BROWSER_EXECUTABLE_PATH
CDP_ENDPOINT = os.getenv("CDP_ENDPOINT") or None

# 课程链接配置
_video_list_url = os.getenv("VIDEO_LIST_URL")
if SKIP_SETUP_WIZARD and (not _video_list_url or "YOUR_COURSE_ID" in _video_list_url):
    # 脚本化模式下严格校验
    raise ValueError(
        "错误: 环境变量 'VIDEO_LIST_URL' 未设置、为空，或仍包含示例值 "
        "'YOUR_COURSE_ID'。脚本化模式（SKIP_SETUP_WIZARD=true）下必须提供有效的课程链接。"
    )
VIDEO_LIST_URL: str = _video_list_url or ""

# 登录配置
LOGIN_MODE = os.getenv("LOGIN_MODE", "cookie").lower()  # cookie/credential/manual
SCNU_USERNAME = os.getenv("SCNU_USERNAME", "")  # 账号（LOGIN_MODE=credential 时必需）
SCNU_PASSWORD = os.getenv("SCNU_PASSWORD", "")  # 密码（LOGIN_MODE=credential 时必需）
SCNU_COOKIES_JSON = os.getenv(
    "SCNU_COOKIES_JSON", ""
)  # Cookie JSON（LOGIN_MODE=manual 时必需）

# 脚本化模式下校验登录配置
if SKIP_SETUP_WIZARD:
    if LOGIN_MODE == "credential" and (not SCNU_USERNAME or not SCNU_PASSWORD):
        raise ValueError(
            "错误: LOGIN_MODE=credential 时必须设置 SCNU_USERNAME 和 SCNU_PASSWORD 环境变量。"
        )
    if LOGIN_MODE == "manual" and not SCNU_COOKIES_JSON:
        raise ValueError(
            "错误: LOGIN_MODE=manual 时必须设置 SCNU_COOKIES_JSON 环境变量。"
        )
    if LOGIN_MODE not in ("cookie", "credential", "manual"):
        raise ValueError(
            f"错误: LOGIN_MODE 必须是 cookie、credential 或 manual 之一，当前值: {LOGIN_MODE}"
        )


# ============= 其他配置 =============
# 测试模式
TEST_LOGIN_MODE = False  # 设置为True以启用登录测试模式（仅测试登录功能）
# Cookie登录配置
COOKIE_FILE = os.getenv("COOKIE_FILE", "cookies.json")  # Cookie文件路径
BASE_URL = "https://moodle.scnu.edu.cn/my/"  # 网站首页URL(用于验证Cookie)
SSO_INDEX_URL = "https://sso.scnu.edu.cn/AccountService/user/index.html"  # SSO主页URL
LOGIN_URL = "https://sso.scnu.edu.cn/AccountService/user/login.html"
# URL模式匹配（脚本会自动找到所有包含此模式的链接）
URL_PATTERN = (
    "https://moodle.scnu.edu.cn/mod/fsresource/view.php?id="  # 视频链接的URL模式
)
# 视频播放配置
VIDEO_ELEMENT_SELECTOR = "video"  # 视频元素的CSS选择器
PLAY_BUTTON_SELECTOR = ".vjs-big-play-button"  # 播放按钮的CSS选择器
DEFAULT_WAIT_TIME = 2  # 如果无法获取视频时长,默认等待时间(秒)
