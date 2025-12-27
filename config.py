"""
配置文件
敏感配置从 .env 文件读取，其他配置在此文件中设置
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# ============= 从环境变量读取的配置 =============
BROWSER = os.getenv("BROWSER", "msedge")  # 浏览器类型(msedge/chrome/firefox)
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"  # 是否使用无头模式
if not (VIDEO_LIST_URL := os.getenv("VIDEO_LIST_URL")):
    raise ValueError("错误: 环境变量 'VIDEO_LIST_URL' 未设置或为空。请在 .env 文件中配置它。")


# ============= 其他配置 =============
# 测试模式
TEST_LOGIN_MODE = False  # 设置为True以启用登录测试模式（仅测试登录功能）
# Cookie登录配置
COOKIE_FILE = "cookies.json"  # Cookie文件路径
BASE_URL = "https://moodle.scnu.edu.cn/my/"  # 网站首页URL(用于验证Cookie)
SSO_INDEX_URL = "https://sso.scnu.edu.cn/AccountService/user/index.html"  # SSO主页URL
LOGIN_URL = "https://sso.scnu.edu.cn/AccountService/user/login.html"
# URL模式匹配（脚本会自动找到所有包含此模式的链接）
URL_PATTERN = "https://moodle.scnu.edu.cn/mod/fsresource/view.php?id="  # 视频链接的URL模式
# 视频播放配置
VIDEO_ELEMENT_SELECTOR = "video"  # 视频元素的CSS选择器
PLAY_BUTTON_SELECTOR = ".vjs-big-play-button"  # 播放按钮的CSS选择器
DEFAULT_WAIT_TIME = 2  # 如果无法获取视频时长,默认等待时间(秒)
