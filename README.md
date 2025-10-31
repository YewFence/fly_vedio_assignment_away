# 视频自动观看脚本

使用 Playwright 自动登录网站、点击视频链接并等待视频播放完成。

## 功能特点

- ✅ 自动登录网站
- ✅ 自动获取页面上的所有视频链接
- ✅ 自动播放视频并等待播放完成
- ✅ 智能检测视频时长(如果无法检测则使用默认等待时间)
- ✅ 显示进度条和实时状态
- ✅ 支持有头/无头模式运行

## 安装步骤

本项目已使用 `uv` 管理依赖,Playwright 和浏览器已安装完成。

## 使用方法

### 第一步:找到网站元素的CSS选择器

1. 打开你的目标网站
2. 按 `F12` 打开浏览器开发者工具
3. 点击左上角的"选择元素"工具(或按 `Ctrl+Shift+C`)
4. 点击页面上的元素(用户名输入框、密码输入框、登录按钮、视频链接等)
5. 在Elements标签中右键该元素 -> `Copy` -> `Copy selector`

### 第二步:配置脚本

编辑 `scripts.py` 文件中的 `main()` 函数里的配置区域:

```python
# 登录配置
LOGIN_URL = "https://your-website.com/login"  # 改为你的登录页面URL
USERNAME = "your_username"  # 改为你的用户名
PASSWORD = "your_password"  # 改为你的密码
USERNAME_SELECTOR = "#username"  # 改为用户名输入框的选择器
PASSWORD_SELECTOR = "#password"  # 改为密码输入框的选择器
SUBMIT_SELECTOR = "button[type='submit']"  # 改为登录按钮的选择器

# 视频列表配置
VIDEO_LIST_URL = "https://your-website.com/videos"  # 改为视频列表页面URL
VIDEO_LINK_SELECTOR = "a.video-link"  # 改为视频链接的选择器

# 视频播放配置
VIDEO_ELEMENT_SELECTOR = "video"  # 视频元素选择器(通常不需要改)
PLAY_BUTTON_SELECTOR = None  # 如果需要点击播放按钮,填写选择器
DEFAULT_WAIT_TIME = 60  # 默认等待时间(秒)
```

### 第三步:运行脚本

```bash
cd school_vedio_hw
uv run python scripts.py
```

## 高级用法

### 1. 使用无头模式(后台运行,不显示浏览器窗口)

在配置区域设置:
```python
HEADLESS = True
```

### 2. 直接指定视频链接列表

如果你不想从页面获取链接,而是想直接指定视频URL,可以修改 `main()` 函数:

```python
# 不使用 get_video_links,直接指定链接
video_links = [
    "https://your-website.com/video/1",
    "https://your-website.com/video/2",
    "https://your-website.com/video/3",
]
```

### 3. 调整等待时间

如果脚本能检测到视频时长,会自动等待相应时间。如果无法检测,会使用 `DEFAULT_WAIT_TIME`。

你可以根据视频实际长度调整这个值:
```python
DEFAULT_WAIT_TIME = 120  # 改为120秒(2分钟)
```

## 常见问题

### Q: 如何找到正确的CSS选择器?

A:
1. 对于输入框:通常是 `input[name="username"]` 或 `#username`
2. 对于按钮:通常是 `button[type="submit"]` 或 `.login-btn`
3. 对于链接:右键点击链接 -> 检查 -> Copy selector

### Q: 登录失败怎么办?

A:
1. 检查用户名、密码是否正确
2. 检查选择器是否正确(用开发者工具验证)
3. 有些网站有验证码,需要手动处理
4. 登录后可能需要等待跳转,调整 `asyncio.sleep(3)` 的时间

### Q: 找不到视频链接怎么办?

A:
1. 确认 `VIDEO_LINK_SELECTOR` 是否正确
2. 可以在浏览器中测试: `document.querySelectorAll('你的选择器')`
3. 有些网站视频是动态加载的,可能需要等待更长时间

### Q: 视频时长检测不到怎么办?

A:
1. 检查 `VIDEO_ELEMENT_SELECTOR` 是否正确
2. 有些网站使用自定义播放器,可能需要修改检测逻辑
3. 使用固定的 `DEFAULT_WAIT_TIME` 也可以

## 脚本说明

### 主要类: `VideoAutomation`

- `setup()`: 启动浏览器
- `login()`: 登录网站
- `get_video_links()`: 获取视频链接列表
- `get_video_duration()`: 获取视频时长
- `play_video()`: 播放单个视频
- `watch_videos()`: 批量观看视频
- `close()`: 关闭浏览器

### 运行流程

1. 启动浏览器
2. 访问登录页面并登录
3. 访问视频列表页面获取所有视频链接
4. 依次访问每个视频页面
5. 检测视频时长并等待播放完成
6. 关闭浏览器

## 注意事项

⚠️ **重要提醒:**
- 请确保你有权限访问和观看这些视频
- 不要用于非法用途
- 某些网站可能有反爬虫机制,使用时请注意
- 建议先用少量视频测试

## 技术支持

如果遇到问题:
1. 检查配置是否正确
2. 查看控制台输出的错误信息
3. 使用 `HEADLESS = False` 查看浏览器实际操作过程
4. 必要时可以添加更多的 `await asyncio.sleep()` 等待页面加载
