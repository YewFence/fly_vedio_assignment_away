# 视频自动观看脚本

使用 Playwright 自动登录网站、点击视频链接并等待视频播放完成。

## 功能特点

- ✅ 自动登录网站（支持Cookie登录）
- ✅ 自动获取页面上的所有视频链接
- ✅ **支持嵌套列表结构（ul > li > ul > li）**
- ✅ **智能排除装饰性元素**
- ✅ 自动播放视频并等待播放完成
- ✅ 智能检测视频时长(如果无法检测则使用默认等待时间)
- ✅ 显示进度条和实时状态
- ✅ 支持有头/无头模式运行
- ✅ **内置页面结构调试工具**
- ✅ **配置与代码分离**

## 📚 快速导航

- **配置文件使用**（必读）→ 查看 [CONFIG_USAGE.md](CONFIG_USAGE.md) ⭐
- **嵌套列表结构**（多层ul/li）→ 查看 [NESTED_LIST_GUIDE.md](NESTED_LIST_GUIDE.md)
- **Cookie登录**（免密码登录）→ 查看 [COOKIE_GUIDE.md](COOKIE_GUIDE.md)
- **快速开始**（新手指南）→ 查看 [QUICK_START.md](QUICK_START.md)

## 安装步骤

本项目已使用 `uv` 管理依赖,Playwright 和浏览器已安装完成。

---

## 🚀 快速开始（4步完成）

### 第一步：获取Cookie

本脚本使用Cookie登录，无需配置用户名密码。

**最简单的方法**：

1. 安装浏览器扩展 [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
2. 在浏览器中登录你的目标网站
3. 点击扩展图标 → Export → JSON
4. 保存为 `cookies.json` 到 `school_vedio_hw` 目录

**详细说明**: [HOW_TO_GET_COOKIES.md](HOW_TO_GET_COOKIES.md) ⭐

### 第二步：创建配置文件

从示例文件复制一份配置文件：

```bash
# Windows
copy config_example.py config.py

# Linux/Mac
cp config_example.py config.py
```

### 第三步：编辑配置

打开 `config.py` 文件，填入你的实际配置：

```python
# Cookie登录
BASE_URL = "https://your-website.com"  # 改为你的网站首页
COOKIE_FILE = "cookies.json"  # Cookie文件路径

# 视频列表配置
VIDEO_LIST_URL = "https://your-website.com/videos"  # 改为视频列表页面URL

# 选择提取模式
EXTRACTION_MODE = "simple"  # "simple" 或 "nested"

# 简单模式（当 EXTRACTION_MODE = "simple" 时）
VIDEO_LINK_SELECTOR = "a.video-link"  # 改为视频链接的选择器

# 嵌套模式（当 EXTRACTION_MODE = "nested" 时）
VIDEO_LI_SELECTOR = "li.video-item"  # 包含视频链接的li选择器
EXCLUDE_CLASS = "decoration"  # 需要排除的li的class
```

**💡 如何找到选择器？**

运行调试工具自动分析页面结构：

```bash
# 先编辑 debug_page.py，填入你的视频列表页面URL
# 然后运行：
uv run python debug_page.py
```

工具会告诉你所有可用的选择器！

详细配置说明：[CONFIG_USAGE.md](CONFIG_USAGE.md)

### 第四步:运行脚本

```bash
cd school_vedio_hw
uv run python scripts.py
```

---

### 方式二：嵌套列表结构（高级）

**如果你的网站视频链接在嵌套的列表中**（例如：主题 > 子主题 > 视频），使用这个方式。

#### 第一步：使用调试工具分析页面结构

编辑 `debug_page.py`：

```python
PAGE_URL = "https://your-website.com/videos"  # 改为你的视频列表页面
```

运行调试工具：

```bash
cd school_vedio_hw
uv run python debug_page.py
```

调试工具会输出详细的页面结构分析，包括：
- 所有 `<ul>` 和 `<li>` 的数量
- 每个 `<li>` 的 class 名称
- `<a>` 标签的分布情况
- 示例链接

#### 第二步：找到正确的选择器

根据调试输出，确定：

1. **包含视频链接的 `<li>` 的选择器**
   - 例如：`li.video-item`、`li.lesson`、`ul.video-list > li`

2. **需要排除的装饰性 `<li>` 的 class**（如果有）
   - 例如：`decoration`、`divider`、`separator`

#### 第三步：配置脚本

编辑 `config.py` 文件：

```python
# 选择嵌套模式
EXTRACTION_MODE = "nested"

# 视频列表配置（嵌套结构）
VIDEO_LIST_URL = "https://your-website.com/videos"
VIDEO_LI_SELECTOR = "li.video-item"  # 包含视频链接的li选择器
EXCLUDE_CLASS = "decoration"  # 需要排除的li的class（如果没有则设为None）
```

**注意**：设置 `EXTRACTION_MODE = "nested"` 后，脚本会自动使用嵌套提取方法。

#### 第四步：运行脚本

```bash
cd school_vedio_hw
uv run python scripts.py
```

**详细指南**：查看 [NESTED_LIST_GUIDE.md](NESTED_LIST_GUIDE.md) 获取完整的嵌套列表使用教程。

---

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
