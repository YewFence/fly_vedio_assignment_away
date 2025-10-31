# 配置文件使用指南

## 🚀 快速开始

### 步骤1: 创建配置文件

从示例文件复制一份配置文件：

```bash
# Windows
copy config_example.py config.py

# Linux/Mac
cp config_example.py config.py
```

### 步骤2: 编辑配置

打开 `config.py` 并填入你的实际配置：

```python
# 登录配置
LOGIN_URL = "https://your-site.com/login"  # 改成你的网站
USERNAME = "your_username"                  # 改成你的用户名
PASSWORD = "your_password"                  # 改成你的密码

# 视频列表配置
VIDEO_LIST_URL = "https://your-site.com/videos"  # 改成视频列表页面

# 选择提取模式
EXTRACTION_MODE = "simple"  # 或 "nested"
```

### 步骤3: 运行脚本

```bash
cd school_vedio_hw
uv run python scripts.py
```

---

## 📋 配置项说明

### 基本配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `USE_COOKIE_LOGIN` | 是否使用Cookie登录 | `True` / `False` |
| `LOGIN_URL` | 登录页面URL | `"https://site.com/login"` |
| `USERNAME` | 用户名 | `"202012345"` |
| `PASSWORD` | 密码 | `"MyPassword"` |
| `VIDEO_LIST_URL` | 视频列表页面URL | `"https://site.com/videos"` |

### 提取模式配置

#### 简单模式 (simple)

适用于简单的列表结构：

```python
EXTRACTION_MODE = "simple"
VIDEO_LINK_SELECTOR = "ul.videos li a"  # 直接选择所有视频链接
```

**示例HTML结构**：
```html
<ul class="videos">
  <li><a href="/video/1">视频1</a></li>
  <li><a href="/video/2">视频2</a></li>
</ul>
```

#### 嵌套模式 (nested)

适用于复杂的嵌套列表结构：

```python
EXTRACTION_MODE = "nested"
VIDEO_LI_SELECTOR = "li.video-item"  # 包含视频的li
EXCLUDE_CLASS = "decoration"         # 需要排除的li的class
```

**示例HTML结构**：
```html
<ul>
  <li class="topic">
    <ul>
      <li class="decoration">--- 视频列表 ---</li>
      <li class="video-item"><a href="/video/1">视频1</a></li>
      <li class="video-item"><a href="/video/2">视频2</a></li>
    </ul>
  </li>
</ul>
```

### 选择器配置

| 配置项 | 说明 | 如何获取 |
|--------|------|----------|
| `USERNAME_SELECTOR` | 用户名输入框选择器 | F12 → 右键用户名框 → Copy selector |
| `PASSWORD_SELECTOR` | 密码输入框选择器 | F12 → 右键密码框 → Copy selector |
| `SUBMIT_SELECTOR` | 登录按钮选择器 | F12 → 右键登录按钮 → Copy selector |
| `VIDEO_LINK_SELECTOR` | 视频链接选择器（简单模式） | 运行 debug_page.py 查看 |
| `VIDEO_LI_SELECTOR` | 包含视频的li选择器（嵌套模式） | 运行 debug_page.py 查看 |
| `EXCLUDE_CLASS` | 需要排除的li的class | 运行 debug_page.py 查看 |

---

## 🔍 如何找到正确的选择器

### 方法1: 使用调试工具（推荐）⭐

1. **编辑** `debug_page.py`：
   ```python
   PAGE_URL = "https://your-site.com/videos"
   ```

2. **运行调试工具**：
   ```bash
   uv run python debug_page.py
   ```

3. **查看输出**，找到：
   - 包含视频的 `<li>` 的 class
   - 需要排除的 `<li>` 的 class
   - 所有可用的选择器

### 方法2: 浏览器开发者工具

1. 打开网站，按 `F12`
2. 按 `Ctrl+Shift+C` 激活元素选择器
3. 点击页面上的元素
4. 查看 HTML 中的 class、id 等
5. 右键 → Copy → Copy selector

### 方法3: Console 测试

在浏览器 Console 中测试：

```javascript
// 测试选择器是否正确
document.querySelectorAll('li.video-item').length

// 查看所有匹配的链接
Array.from(document.querySelectorAll('li.video-item a')).map(a => a.href)
```

---

## 📝 配置示例

### 示例1: 学校网站（嵌套列表）

```python
# config.py

# Cookie登录
USE_COOKIE_LOGIN = True
BASE_URL = "https://school.edu"

# 登录配置
LOGIN_URL = "https://school.edu/login"
USERNAME = "202012345"
PASSWORD = "MyPassword123"
USERNAME_SELECTOR = "input[name='username']"
PASSWORD_SELECTOR = "input[name='password']"
SUBMIT_SELECTOR = "button.login-btn"

# 视频列表（嵌套模式）
VIDEO_LIST_URL = "https://school.edu/course/python-101"
EXTRACTION_MODE = "nested"
VIDEO_LI_SELECTOR = "li.lesson-item"
EXCLUDE_CLASS = "section-header"

# 视频播放
VIDEO_ELEMENT_SELECTOR = "video"
PLAY_BUTTON_SELECTOR = None
DEFAULT_WAIT_TIME = 60

# 浏览器
HEADLESS = False
```

### 示例2: 培训平台（简单列表）

```python
# config.py

# Cookie登录
USE_COOKIE_LOGIN = True
BASE_URL = "https://learning.com"

# 登录配置
LOGIN_URL = "https://learning.com/signin"
USERNAME = "user@email.com"
PASSWORD = "SecretPass456"
USERNAME_SELECTOR = "#email"
PASSWORD_SELECTOR = "#password"
SUBMIT_SELECTOR = "button[type='submit']"

# 视频列表（简单模式）
VIDEO_LIST_URL = "https://learning.com/course/123"
EXTRACTION_MODE = "simple"
VIDEO_LINK_SELECTOR = "div.course-content ul li a"

# 视频播放
VIDEO_ELEMENT_SELECTOR = "video"
PLAY_BUTTON_SELECTOR = "button.play-button"
DEFAULT_WAIT_TIME = 120

# 浏览器
HEADLESS = False
```

---

## ⚙️ 高级配置

### Cookie 登录

Cookie登录可以省略每次输入用户名密码：

```python
USE_COOKIE_LOGIN = True  # 启用Cookie登录
COOKIE_FILE = "cookies.json"  # Cookie保存位置
```

**工作流程**：
1. 首次运行：用账号密码登录，自动保存Cookie
2. 后续运行：自动使用Cookie登录
3. Cookie过期：自动切换到密码登录

详细说明见 [COOKIE_GUIDE.md](COOKIE_GUIDE.md)

### 无头模式

后台运行，不显示浏览器窗口：

```python
HEADLESS = True
```

适合：
- 服务器上运行
- 后台挂机
- 提高性能

### 视频播放按钮

如果视频需要手动点击播放：

```python
PLAY_BUTTON_SELECTOR = "button.play-btn"  # 播放按钮选择器
```

如果视频自动播放：

```python
PLAY_BUTTON_SELECTOR = None
```

### 等待时间

如果无法检测视频时长，会使用默认等待时间：

```python
DEFAULT_WAIT_TIME = 120  # 等待120秒（2分钟）
```

---

## 🔒 安全注意事项

### 1. 保护配置文件

`config.py` 包含你的用户名和密码，**不要分享或上传到网上**！

- ✅ `config.py` 已自动添加到 `.gitignore`
- ✅ Git 不会提交这个文件
- ⚠️ 不要手动 `git add config.py`

### 2. Cookie 安全

Cookie 文件也包含登录凭证：

- ✅ `cookies.json` 已自动添加到 `.gitignore`
- ⚠️ 不要分享 Cookie 文件
- ⚠️ 定期删除过期的 Cookie

### 3. 密码管理

建议：
- 使用专用密码，不要用常用密码
- 定期更换密码
- 如果担心安全，每次运行后删除 `config.py`

---

## ❓ 常见问题

### Q: 运行脚本提示找不到 config.py？

**A:** 你需要先创建配置文件：

```bash
copy config_example.py config.py  # Windows
cp config_example.py config.py    # Linux/Mac
```

然后编辑 `config.py` 填入你的配置。

### Q: 如何知道用简单模式还是嵌套模式？

**A:** 运行调试工具查看页面结构：

```bash
uv run python debug_page.py
```

如果输出显示有多层嵌套的 `<ul>` 和 `<li>`，使用嵌套模式。
如果是简单的列表，使用简单模式。

详细说明见 [NESTED_LIST_GUIDE.md](NESTED_LIST_GUIDE.md)

### Q: 选择器填错了怎么办？

**A:**
1. 重新编辑 `config.py` 修改选择器
2. 保存后重新运行 `uv run python scripts.py`
3. 使用 `debug_page.py` 验证选择器

### Q: 可以修改 config_example.py 吗？

**A:**
- `config_example.py` 是示例文件，**不要修改它**
- 你应该修改 `config.py`
- `config_example.py` 用于参考和备份

### Q: 如何重置配置？

**A:** 重新从示例复制一份：

```bash
copy config_example.py config.py  # 会提示覆盖，输入 Y
```

---

## 📚 相关文档

- **README.md** - 项目总体介绍
- **QUICK_START.md** - 快速开始指南
- **NESTED_LIST_GUIDE.md** - 嵌套列表详细教程
- **COOKIE_GUIDE.md** - Cookie登录指南
- **config_example.py** - 配置示例文件

---

## 🎯 使用流程

```
1. 创建配置文件
   copy config_example.py config.py
   ↓

2. 编辑配置
   填入网站URL、用户名、密码等
   ↓

3. 找到选择器（可选）
   uv run python debug_page.py
   ↓

4. 运行脚本
   uv run python scripts.py
   ↓

5. 完成！
   自动登录 → 提取链接 → 观看视频
```

---

现在就开始配置吧！🚀

1. `copy config_example.py config.py`
2. 编辑 `config.py`
3. `uv run python scripts.py`
