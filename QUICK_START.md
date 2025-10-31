# 🎯 快速使用指南

## 你的网站是哪种类型？

### 类型一：简单列表 ⭐ 新手推荐

**页面结构**：
```html
<ul>
  <li><a href="/video/1">视频1</a></li>
  <li><a href="/video/2">视频2</a></li>
  <li><a href="/video/3">视频3</a></li>
</ul>
```

**使用方法**：
1. 查看 [README.md](README.md) → 方式一
2. 配置 `VIDEO_LINK_SELECTOR = "ul li a"`
3. 运行 `uv run python scripts.py`

---

### 类型二：嵌套列表 🔥 你的情况

**页面结构**：
```html
<ul class="主题列表">
  <li class="主题">
    <h3>主题1</h3>
    <ul class="视频列表">
      <li class="decoration">装饰文字</li>
      <li class="video-item">
        <a href="/video/1">视频1</a>
      </li>
      <li class="video-item">
        <a href="/video/2">视频2</a>
      </li>
    </ul>
  </li>
  <li class="主题">
    <h3>主题2</h3>
    <ul class="视频列表">
      <li class="video-item">
        <a href="/video/3">视频3</a>
      </li>
    </ul>
  </li>
</ul>
```

**使用方法**：

#### 步骤1：调试页面结构

```bash
# 编辑 debug_page.py
# 修改 PAGE_URL = "你的视频列表页面URL"

# 运行调试
cd school_vedio_hw
uv run python debug_page.py
```

你会看到类似这样的输出：

```
======================================================================
页面结构分析报告
======================================================================

📊 统计信息:
  - 找到 3 个 <ul> 元素
  - 所有 <a> 标签总数: 15
  - 发现的li class类型: video-item, decoration, topic-header

📋 UL详细结构:

  UL #0:
    - Class: 'topic-list'
    - 直接子li数量: 2

      LI #0:
        - Classes: topic
        - 包含的<a>数量: 5
        - 嵌套的<ul>数量: 1
        - 示例链接: https://example.com/video/1...

      LI #1:
        - Classes: decoration
        - 包含的<a>数量: 0
        - 嵌套的<ul>数量: 0
======================================================================
```

#### 步骤2：确定选择器

根据调试输出，你需要：

1. **找到包含视频的li的class**
   - 在上面的例子中是：`video-item`
   - 所以选择器是：`li.video-item`

2. **找到需要排除的li的class**（如果有）
   - 在上面的例子中是：`decoration`

#### 步骤3：配置主脚本

编辑 `scripts.py` 的 `main()` 函数：

```python
async def main():
    # Cookie登录配置（推荐）
    USE_COOKIE_LOGIN = True
    COOKIE_FILE = "cookies.json"
    BASE_URL = "https://your-school.com"  # 改成你的网站

    # 登录配置
    LOGIN_URL = "https://your-school.com/login"  # 改成你的登录页面
    USERNAME = "your_student_id"  # 改成你的用户名
    PASSWORD = "your_password"  # 改成你的密码
    USERNAME_SELECTOR = "#username"  # 改成实际的选择器
    PASSWORD_SELECTOR = "#password"  # 改成实际的选择器
    SUBMIT_SELECTOR = "button[type='submit']"  # 改成实际的选择器

    # 视频列表配置（关键！）
    VIDEO_LIST_URL = "https://your-school.com/course/123"  # 改成视频列表页面
    VIDEO_LI_SELECTOR = "li.video-item"  # 改成你找到的选择器
    EXCLUDE_CLASS = "decoration"  # 改成需要排除的class，没有就写 None

    # 视频播放配置
    VIDEO_ELEMENT_SELECTOR = "video"
    PLAY_BUTTON_SELECTOR = None  # 如果需要点击播放按钮，填写选择器
    DEFAULT_WAIT_TIME = 60  # 如果检测不到视频时长，等待多少秒

    # 浏览器配置
    HEADLESS = False  # False=显示浏览器，True=后台运行

    # ========== 下面的代码不要改 ==========
    automation = VideoAutomation(headless=HEADLESS)

    try:
        await automation.setup()

        # 登录
        login_success = False
        if USE_COOKIE_LOGIN:
            login_success = await automation.login_with_cookies(BASE_URL, COOKIE_FILE)
        if not login_success:
            await automation.login(
                LOGIN_URL, USERNAME, PASSWORD,
                USERNAME_SELECTOR, PASSWORD_SELECTOR, SUBMIT_SELECTOR,
                save_cookies=True, cookie_file=COOKIE_FILE
            )

        # 提取视频链接（使用嵌套方法）
        video_links = await automation.get_nested_video_links(
            VIDEO_LIST_URL,
            VIDEO_LI_SELECTOR,
            EXCLUDE_CLASS
        )

        # 观看视频
        if video_links:
            await automation.watch_videos(
                video_links,
                VIDEO_ELEMENT_SELECTOR,
                PLAY_BUTTON_SELECTOR,
                DEFAULT_WAIT_TIME
            )
        else:
            print("⚠ 没有找到视频链接")

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await automation.close()
```

#### 步骤4：运行脚本

```bash
cd school_vedio_hw
uv run python scripts.py
```

---

## 🔍 如何找到CSS选择器？

### 方法1：使用浏览器开发者工具

1. 打开网站，按 `F12`
2. 点击 Elements 标签左上角的"选择元素"按钮（或按 `Ctrl+Shift+C`）
3. 点击页面上的视频链接
4. 在 Elements 中会高亮显示对应的HTML代码
5. 查看 `<li>` 的 class 属性

**示例**：
```html
<li class="video-item active">  <!-- class="video-item active" -->
  <a href="/video/1">视频1</a>
</li>
```
→ 选择器是：`li.video-item` 或 `li.active` 或 `li.video-item.active`

### 方法2：在浏览器Console中测试

1. 按 `F12` 打开开发者工具
2. 切换到 Console 标签
3. 输入以下命令测试选择器：

```javascript
// 测试选择器
document.querySelectorAll('li.video-item').length  // 应该返回视频数量

// 查看所有链接
Array.from(document.querySelectorAll('li.video-item a')).map(a => a.href)

// 测试排除
Array.from(document.querySelectorAll('li'))
  .filter(li => !li.classList.contains('decoration'))
  .length
```

### 方法3：使用调试工具（最简单）⭐

直接运行 `uv run python debug_page.py`，工具会自动分析并告诉你所有可用的选择器！

---

## 📝 配置示例

### 示例1：学校网站

```python
# 登录
LOGIN_URL = "https://school.edu/login"
USERNAME = "202012345"  # 学号
PASSWORD = "MyPassword123"
USERNAME_SELECTOR = "input[name='username']"
PASSWORD_SELECTOR = "input[name='password']"
SUBMIT_SELECTOR = "button.login-btn"

# 视频
VIDEO_LIST_URL = "https://school.edu/course/python-101"
VIDEO_LI_SELECTOR = "li.lesson-item"
EXCLUDE_CLASS = "section-header"
```

### 示例2：培训平台

```python
# 登录
LOGIN_URL = "https://learning-platform.com/signin"
USERNAME = "user@email.com"
PASSWORD = "SecretPass456"
USERNAME_SELECTOR = "#email"
PASSWORD_SELECTOR = "#password"
SUBMIT_SELECTOR = "button[type='submit']"

# 视频
VIDEO_LIST_URL = "https://learning-platform.com/courses/123/lessons"
VIDEO_LI_SELECTOR = "div.course-content li.video"
EXCLUDE_CLASS = None  # 没有需要排除的
```

---

## ⚡ 常见问题速查

### Q: 找不到视频链接？
**A:**
1. 运行 `uv run python debug_page.py` 查看页面结构
2. 在浏览器Console测试选择器
3. 确保已登录（先登录再访问视频列表页面）

### Q: 提取了错误的链接？
**A:**
1. 检查选择器是否太宽泛（如只用 `li` 而不是 `li.video-item`）
2. 使用 `EXCLUDE_CLASS` 排除装饰性元素
3. 在Console测试：`document.querySelectorAll('你的选择器')`

### Q: 视频没有自动播放？
**A:**
1. 设置 `PLAY_BUTTON_SELECTOR`，填入播放按钮的选择器
2. 增加等待时间 `DEFAULT_WAIT_TIME`
3. 在浏览器中手动检查视频播放器

### Q: Cookie登录失败？
**A:**
1. Cookie可能已过期，删除 `cookies.json`
2. 用账号密码重新登录，会自动生成新Cookie
3. 查看 [COOKIE_GUIDE.md](COOKIE_GUIDE.md)

---

## 📚 完整文档

- **README.md** - 总体介绍和基础使用
- **NESTED_LIST_GUIDE.md** - 嵌套列表详细教程 ⭐ 推荐阅读
- **COOKIE_GUIDE.md** - Cookie登录完整指南
- **config_example.py** - 配置示例文件

---

## 🎉 开始使用

1. ✅ 运行 `uv run python debug_page.py` 分析页面
2. ✅ 找到正确的选择器
3. ✅ 配置 `scripts.py`
4. ✅ 运行 `uv run python scripts.py`
5. ✅ 坐下来喝杯咖啡，让脚本自动完成工作！☕

需要帮助？查看详细文档或在Issues中提问！
