"""
配置文件示例
请复制此文件为 config.py 并填入实际的配置信息

命令: cp config_example.py config.py  (Linux/Mac)
命令: copy config_example.py config.py  (Windows)
"""

# ============= Cookie登录配置 =============
USE_COOKIE_LOGIN = True  # 是否使用Cookie登录(推荐)
COOKIE_FILE = "cookies.json"  # Cookie文件路径
BASE_URL = "https://example.com"  # 网站首页URL(用于验证Cookie)

# ============= 登录配置(仅在Cookie登录失败时使用) =============
LOGIN_URL = "https://example.com/login"  # 登录页面URL
USERNAME = "your_username"  # 你的用户名
PASSWORD = "your_password"  # 你的密码
USERNAME_SELECTOR = "#username"  # 用户名输入框选择器
PASSWORD_SELECTOR = "#password"  # 密码输入框选择器
SUBMIT_SELECTOR = "button[type='submit']"  # 登录按钮选择器

# ============= 视频列表配置 =============
VIDEO_LIST_URL = "https://example.com/videos"  # 视频列表页面URL

# 选择模式：
# - "simple": 简单模式，直接使用 VIDEO_LINK_SELECTOR 选择所有链接
# - "nested": 嵌套模式，使用 VIDEO_LI_SELECTOR 和 EXCLUDE_CLASS 处理嵌套列表
EXTRACTION_MODE = "simple"  # "simple" 或 "nested"

# 简单模式配置（当 EXTRACTION_MODE = "simple" 时使用）
VIDEO_LINK_SELECTOR = "a.video-link"  # 视频链接的CSS选择器

# 嵌套模式配置（当 EXTRACTION_MODE = "nested" 时使用）
VIDEO_LI_SELECTOR = "li.video-item"  # 包含视频链接的li的CSS选择器
EXCLUDE_CLASS = None  # 需要排除的li的class名称（装饰性元素），没有则设为None

# ============= 视频播放配置 =============
VIDEO_ELEMENT_SELECTOR = "video"  # 视频元素的CSS选择器
PLAY_BUTTON_SELECTOR = None  # 播放按钮的CSS选择器(如果不需要点击则设为None)
DEFAULT_WAIT_TIME = 60  # 如果无法获取视频时长,默认等待时间(秒)

# ============= 浏览器配置 =============
HEADLESS = False  # 是否使用无头模式(True=不显示浏览器窗口, False=显示浏览器)


# ============= 配置说明 =============
"""
如何找到CSS选择器？

方法1: 使用调试工具（推荐）⭐
  运行: uv run python debug_page.py
  工具会自动分析页面结构并给出建议

方法2: 使用浏览器开发者工具
  1. 打开网站，按 F12
  2. 按 Ctrl+Shift+C 激活元素选择器
  3. 点击页面上的元素
  4. 在 Elements 标签中查看元素的 class、id 等属性
  5. 右键元素 -> Copy -> Copy selector

方法3: 在浏览器Console中测试
  document.querySelectorAll('你的选择器')

常见选择器示例:
  - ID选择器: #username, #password
  - Class选择器: .video-link, .video-item
  - 标签选择器: video, button, input
  - 属性选择器: input[type="text"], button[type="submit"]
  - 组合选择器: ul.video-list > li.video-item

配置示例:

  示例1: 简单列表
    EXTRACTION_MODE = "simple"
    VIDEO_LINK_SELECTOR = "ul.videos li a"

  示例2: 嵌套列表
    EXTRACTION_MODE = "nested"
    VIDEO_LI_SELECTOR = "li.video-item"
    EXCLUDE_CLASS = "decoration"

  示例3: 学校网站
    LOGIN_URL = "https://school.edu/login"
    USERNAME = "202012345"
    PASSWORD = "MyPassword123"
    USERNAME_SELECTOR = "input[name='username']"
    PASSWORD_SELECTOR = "input[name='password']"
    SUBMIT_SELECTOR = "button.login-btn"
    VIDEO_LIST_URL = "https://school.edu/course/python-101"
    EXTRACTION_MODE = "nested"
    VIDEO_LI_SELECTOR = "li.lesson-item"
    EXCLUDE_CLASS = "section-header"
"""
