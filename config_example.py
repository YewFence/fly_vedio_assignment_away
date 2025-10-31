"""
配置文件示例
请复制此文件为 config.py 并填入实际的配置信息

命令: cp config_example.py config.py  (Linux/Mac)
命令: copy config_example.py config.py  (Windows)
"""

# ============= Cookie登录配置 =============
COOKIE_FILE = "cookies.json"  # Cookie文件路径
BASE_URL = "https://moodle.scnu.edu.cn"  # 网站首页URL(用于验证Cookie)

# ============= 视频列表配置 =============
VIDEO_LIST_URL = "https://moodle.scnu.edu.cn/course/view.php?id=YOUR_COURSE_ID"  # 视频列表页面URL

# URL模式匹配（脚本会自动找到所有包含此模式的链接）
URL_PATTERN = "https://moodle.scnu.edu.cn/mod/fsresource/view.php?id="  # 视频链接的URL模式

# ============= 视频播放配置 =============
VIDEO_ELEMENT_SELECTOR = "video"  # 视频元素的CSS选择器
PLAY_BUTTON_SELECTOR = None  # 播放按钮的CSS选择器(如果不需要点击则设为None)
DEFAULT_WAIT_TIME = 60  # 如果无法获取视频时长,默认等待时间(秒)

# ============= 浏览器配置 =============
HEADLESS = False  # 是否使用无头模式(True=不显示浏览器窗口, False=显示浏览器)


# ============= 配置说明 =============
"""
如何配置？

1. 获取Cookie
   - 使用浏览器扩展导出Cookie到 cookies.json
   - 详见: HOW_TO_GET_COOKIES.md

2. 配置网站URL
   - BASE_URL: 网站首页URL，用于Cookie验证
   - VIDEO_LIST_URL: 包含视频链接的课程页面URL
     例如: https://moodle.scnu.edu.cn/course/view.php?id=12345

   如何找到课程ID？
   - 登录Moodle
   - 进入你的课程页面
   - 查看浏览器地址栏，找到 "id=" 后面的数字
   - 例如: https://moodle.scnu.edu.cn/course/view.php?id=12345
     这里的 12345 就是课程ID

3. 配置URL模式
   - URL_PATTERN: 视频链接的URL模式
   - 脚本会自动在页面中查找所有包含此模式的链接
   - 默认值适用于华南师范大学Moodle系统

   如何找到URL模式？
   - 在浏览器中访问课程页面
   - 右键点击任意视频链接 -> 复制链接地址
   - 找出链接中的固定部分（不包括最后的ID数字）
   - 将固定部分填入 URL_PATTERN

   示例:
   如果视频链接是: https://moodle.scnu.edu.cn/mod/fsresource/view.php?id=123456
   那么 URL_PATTERN 应该是: "https://moodle.scnu.edu.cn/mod/fsresource/view.php?id="

   其他常见Moodle URL模式:
   - 资源类型: "/mod/resource/view.php?id="
   - 页面类型: "/mod/page/view.php?id="
   - URL类型: "/mod/url/view.php?id="

4. 视频播放配置
   - VIDEO_ELEMENT_SELECTOR: 视频标签选择器，通常不需要修改
   - PLAY_BUTTON_SELECTOR: 如果视频需要点击播放按钮，填写按钮选择器
   - DEFAULT_WAIT_TIME: 无法检测视频时长时的默认等待时间（秒）

5. 浏览器配置
   - HEADLESS = False: 显示浏览器窗口（推荐，方便调试）
   - HEADLESS = True: 无头模式，后台运行（适合服务器）

完整配置示例（华南师范大学）:
  BASE_URL = "https://moodle.scnu.edu.cn"
  VIDEO_LIST_URL = "https://moodle.scnu.edu.cn/course/view.php?id=12345"
  URL_PATTERN = "https://moodle.scnu.edu.cn/mod/fsresource/view.php?id="
  COOKIE_FILE = "cookies.json"

  # 视频播放
  VIDEO_ELEMENT_SELECTOR = "video"
  PLAY_BUTTON_SELECTOR = None
  DEFAULT_WAIT_TIME = 60

  # 浏览器
  HEADLESS = False

注意事项:
  1. 本脚本仅支持Cookie登录
  2. Cookie会过期，过期后需要重新获取
  3. 确保填写正确的课程ID
  4. URL_PATTERN 必须精确匹配视频链接格式
  5. 查看 HOW_TO_GET_COOKIES.md 了解如何获取Cookie
"""
