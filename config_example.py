"""
配置文件示例
请复制此文件为 config.py 并填入实际的配置信息
"""

# ============= 必须配置 =============
VIDEO_LIST_URL = "https://moodle.scnu.edu.cn/course/view.php?id=YOUR_COURSE_ID"  # 课程链接页面URL


# ============= 可选配置 =============
# 浏览器
BROWSER = "msedge"  # 浏览器类型(msedge/chrome/firefox)
# Cookie登录配置
COOKIE_FILE = "cookies.json"  # Cookie文件路径
BASE_URL = "https://moodle.scnu.edu.cn"  # 网站首页URL(用于验证Cookie)
# URL模式匹配（脚本会自动找到所有包含此模式的链接）
URL_PATTERN = "https://moodle.scnu.edu.cn/mod/fsresource/view.php?id="  # 视频链接的URL模式
# 视频播放配置
VIDEO_ELEMENT_SELECTOR = "video"  # 视频元素的CSS选择器
PLAY_BUTTON_SELECTOR = ".vjs-big-play-button"  # 播放按钮的CSS选择器
DEFAULT_WAIT_TIME = 2  # 如果无法获取视频时长,默认等待时间(秒)
# 浏览器配置
HEADLESS = False  # 是否使用无头模式(True=不显示浏览器窗口, False=显示浏览器)
