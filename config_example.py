"""
配置文件示例
复制此文件为 config.py 并填入实际的配置信息
"""

# ============= 登录配置 =============
LOGIN_URL = "https://example.com/login"  # 登录页面URL
USERNAME = "your_username"  # 你的用户名
PASSWORD = "your_password"  # 你的密码

# 登录页面元素选择器
# 提示: 使用浏览器开发者工具(F12)查找元素的CSS选择器
USERNAME_SELECTOR = "#username"  # 用户名输入框
PASSWORD_SELECTOR = "#password"  # 密码输入框
SUBMIT_SELECTOR = "button[type='submit']"  # 登录按钮

# ============= 视频列表配置 =============
VIDEO_LIST_URL = "https://example.com/videos"  # 包含视频链接的页面URL
VIDEO_LINK_SELECTOR = "a.video-link"  # 视频链接的CSS选择器

# 如果你想指定具体的视频URL列表,可以直接在这里列出:
# VIDEO_LINKS = [
#     "https://example.com/video/1",
#     "https://example.com/video/2",
#     "https://example.com/video/3",
# ]

# ============= 视频播放配置 =============
VIDEO_ELEMENT_SELECTOR = "video"  # 视频元素的CSS选择器
PLAY_BUTTON_SELECTOR = None  # 播放按钮选择器(如果视频自动播放则设为None)
# PLAY_BUTTON_SELECTOR = "button.play-btn"  # 示例:需要点击播放按钮

DEFAULT_WAIT_TIME = 60  # 如果无法获取视频时长,默认等待时间(秒)

# ============= 浏览器配置 =============
HEADLESS = False  # False=显示浏览器窗口, True=无头模式(后台运行)


# ============= 如何找到CSS选择器? =============
# 1. 打开网站并按F12打开开发者工具
# 2. 点击左上角的"选择元素"工具(或按Ctrl+Shift+C)
# 3. 点击页面上你想要定位的元素(如用户名输入框、视频链接等)
# 4. 在开发者工具的Elements标签中会高亮显示该元素的HTML代码
# 5. 右键该元素 -> Copy -> Copy selector,即可获得CSS选择器
#
# 常见选择器示例:
# - ID选择器: #username, #password
# - 类选择器: .video-link, .play-button
# - 标签选择器: video, button, input
# - 属性选择器: input[type="text"], button[type="submit"]
# - 组合选择器: div.container > a.video-link
