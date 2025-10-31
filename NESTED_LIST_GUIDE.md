# 嵌套列表视频提取使用指南

## 📋 你的网页结构

根据你的描述，网页结构如下：

```html
<ul class="主题列表">
  <li class="主题">
    <h3>主题1</h3>
    <ul class="视频列表">
      <li class="decoration">装饰性内容（需要忽略）</li>
      <li class="video-item">
        <div class="video-wrapper">
          <a href="/video/1">视频标题1</a>
        </div>
      </li>
      <li class="video-item">
        <div class="video-wrapper">
          <a href="/video/2">视频标题2</a>
        </div>
      </li>
    </ul>
  </li>

  <li class="主题">
    <h3>主题2</h3>
    <ul class="视频列表">
      <li class="video-item">
        <div class="video-wrapper">
          <a href="/video/3">视频标题3</a>
        </div>
      </li>
    </ul>
  </li>
</ul>
```

## 🔍 第一步：分析页面结构

使用调试工具来分析页面结构：

### 1. 配置调试脚本

编辑 `debug_page.py` 文件：

```python
PAGE_URL = "你的视频列表页面URL"  # 改成实际的URL
```

### 2. 运行调试脚本

```bash
cd school_vedio_hw
uv run python debug_page.py
```

### 3. 查看分析报告

脚本会输出类似这样的报告：

```
======================================================================
页面结构分析报告
======================================================================

📊 统计信息:
  - 找到 5 个 <ul> 元素
  - 所有 <a> 标签总数: 24
  - 发现的li class类型: video-item, decoration, topic-header

📋 UL详细结构:

  UL #0:
    - Class: 'topic-list'
    - ID: 'main-topics'
    - 直接子li数量: 3

      LI #0:
        - Classes: topic
        - 包含的<a>数量: 8
        - 嵌套的<ul>数量: 1
        - 示例链接: https://example.com/video/1...

      LI #1:
        - Classes: topic
        - 包含的<a>数量: 5
        - 嵌套的<ul>数量: 1
        - 示例链接: https://example.com/video/9...

💡 建议:
  根据上面的分析，尝试使用以下选择器:
  - 如果视频链接的li有特定class，使用: 'li.{class_name}'
  - 如果需要排除装饰性li，使用exclude_class参数
======================================================================
```

## ✏️ 第二步：找到正确的CSS选择器

根据调试报告，你需要确定：

### 1. 包含视频链接的 `<li>` 的选择器

常见情况：

| 情况 | 选择器示例 | 说明 |
|------|-----------|------|
| li有特定class | `li.video-item` | 最准确 |
| li在特定ul下 | `ul.video-list > li` | 需要知道ul的class |
| 嵌套在主题下 | `li.topic ul li` | 多层嵌套 |
| 所有包含a标签的li | `li:has(a)` | 使用CSS伪类 |

### 2. 需要排除的 `<li>` 的class

如果有装饰性的li需要忽略，记下它们的class名称，例如：
- `decoration`
- `separator`
- `header`
- `divider`

### 3. 手动验证选择器

在浏览器开发者工具的Console中测试：

```javascript
// 测试选择器是否正确
document.querySelectorAll('li.video-item').length

// 查看是否包含正确的链接
document.querySelectorAll('li.video-item a').forEach(a => {
    console.log(a.href);
});
```

## 🚀 第三步：配置主脚本

### 方式一：使用 `get_nested_video_links`（推荐）

编辑 `scripts.py` 的 `main()` 函数：

```python
async def main():
    # ... 登录配置 ...

    # 视频列表配置（嵌套结构）
    VIDEO_LIST_URL = "https://example.com/videos"

    # 方法1: 只指定包含视频的li
    VIDEO_LI_SELECTOR = "li.video-item"  # 改成你的li选择器
    EXCLUDE_CLASS = None  # 如果不需要排除，设为None

    # 方法2: 如果需要排除装饰性li
    VIDEO_LI_SELECTOR = "ul.video-list > li"  # 更具体的选择器
    EXCLUDE_CLASS = "decoration"  # 需要排除的class名称

    # ... 其他配置 ...

    try:
        await automation.setup()

        # 登录...

        # 使用嵌套提取方法
        video_links = await automation.get_nested_video_links(
            VIDEO_LIST_URL,
            VIDEO_LI_SELECTOR,
            EXCLUDE_CLASS
        )

        # 观看视频...
```

### 方式二：使用简单的选择器

如果你能直接定位到所有 `<a>` 标签：

```python
# 在 main() 函数中

VIDEO_LIST_URL = "https://example.com/videos"
VIDEO_LINK_SELECTOR = "li.video-item a"  # 直接选择所有视频链接

# 使用简单方法
video_links = await automation.get_video_links(
    VIDEO_LIST_URL,
    VIDEO_LINK_SELECTOR
)
```

## 📝 完整示例配置

假设你的页面结构是：

```html
<div id="content">
  <ul class="course-topics">
    <li class="topic-item">
      <h3>第一章</h3>
      <ul class="lesson-list">
        <li class="divider">--- 视频列表 ---</li>
        <li class="lesson">
          <a href="/watch/1">1.1 介绍</a>
        </li>
        <li class="lesson">
          <a href="/watch/2">1.2 基础</a>
        </li>
      </ul>
    </li>
  </ul>
</div>
```

### 调试配置

```python
# debug_page.py
PAGE_URL = "https://your-school.com/course/123"
CONTAINER_SELECTOR = "#content"  # 只分析content区域
```

### 主脚本配置

```python
# scripts.py 中的 main() 函数

# 登录配置
LOGIN_URL = "https://your-school.com/login"
USERNAME = "your_student_id"
PASSWORD = "your_password"
USERNAME_SELECTOR = "input[name='username']"
PASSWORD_SELECTOR = "input[name='password']"
SUBMIT_SELECTOR = "button[type='submit']"

# 视频列表配置
VIDEO_LIST_URL = "https://your-school.com/course/123"
VIDEO_LI_SELECTOR = "li.lesson"  # 只选择lesson类的li
EXCLUDE_CLASS = "divider"  # 排除divider类的li

# 使用嵌套方法
video_links = await automation.get_nested_video_links(
    VIDEO_LIST_URL,
    VIDEO_LI_SELECTOR,
    EXCLUDE_CLASS
)
```

## 🎯 常见CSS选择器速查

| 选择器 | 说明 | 示例 |
|--------|------|------|
| `.class` | 选择特定class | `li.video-item` |
| `#id` | 选择特定id | `#video-list` |
| `element` | 选择标签 | `li`, `a` |
| `parent > child` | 直接子元素 | `ul > li` |
| `ancestor descendant` | 所有后代 | `ul li` |
| `element.class` | 同时满足 | `li.video-item` |
| `element:not(.class)` | 排除class | `li:not(.decoration)` |
| `element:has(selector)` | 包含子元素 | `li:has(a)` |

## 🐛 调试技巧

### 技巧1：在浏览器Console中测试

```javascript
// 测试选择器
document.querySelectorAll('li.video-item')

// 查看匹配元素数量
document.querySelectorAll('li.video-item').length

// 获取所有链接
Array.from(document.querySelectorAll('li.video-item a')).map(a => a.href)

// 排除特定class
Array.from(document.querySelectorAll('li')).filter(li => !li.classList.contains('decoration'))
```

### 技巧2：使用浏览器开发者工具

1. 按 `F12` 打开开发者工具
2. 按 `Ctrl+Shift+C` 激活元素选择器
3. 点击页面上的视频链接
4. 在Elements标签中查看HTML结构
5. 右键元素 → Copy → Copy selector

### 技巧3：逐步缩小范围

```python
# 先从大范围开始
VIDEO_LI_SELECTOR = "li"  # 获取所有li

# 然后缩小到特定区域
VIDEO_LI_SELECTOR = "ul.video-list li"  # ul下的li

# 最后精确到特定class
VIDEO_LI_SELECTOR = "ul.video-list li.video-item"  # 最精确
```

## ⚙️ 高级用法

### 只提取特定主题的视频

如果你只想观看某个主题下的视频：

```python
# 使用更精确的选择器
VIDEO_LI_SELECTOR = "li.topic:nth-child(1) ul li.video-item"  # 只选第一个主题
```

### 自定义链接过滤

如果需要更复杂的过滤逻辑，修改 `get_nested_video_links` 方法或者在获取链接后手动过滤：

```python
video_links = await automation.get_nested_video_links(
    VIDEO_LIST_URL,
    VIDEO_LI_SELECTOR,
    EXCLUDE_CLASS
)

# 手动过滤
video_links = [link for link in video_links if '/watch/' in link]
video_links = video_links[:10]  # 只观看前10个
```

### 处理动态加载的内容

如果页面使用JavaScript动态加载内容：

```python
# 在 get_nested_video_links 前添加等待
await automation.page.goto(VIDEO_LIST_URL, wait_until='networkidle')
await asyncio.sleep(5)  # 额外等待5秒让内容加载

# 或者等待特定元素出现
await automation.page.wait_for_selector('li.video-item', timeout=10000)
```

## 📊 运行流程

```
第一步: 运行调试脚本
┌─────────────────────────┐
│ uv run python debug_page.py │
└─────────────────────────┘
            ↓
    查看页面结构分析报告
            ↓
    找到正确的CSS选择器
            ↓

第二步: 配置主脚本
┌─────────────────────────┐
│   编辑 scripts.py       │
│   - 填写登录信息         │
│   - 填写选择器          │
└─────────────────────────┘
            ↓

第三步: 运行主脚本
┌─────────────────────────┐
│ uv run python scripts.py│
└─────────────────────────┘
            ↓
    自动登录 → 提取链接 → 观看视频
```

## 🔥 快速开始示例

假设你已经知道选择器，快速配置：

```python
# scripts.py 主要配置部分

async def main():
    # Cookie登录
    USE_COOKIE_LOGIN = True
    COOKIE_FILE = "cookies.json"
    BASE_URL = "https://your-school.com"

    # 账号密码（首次需要）
    LOGIN_URL = "https://your-school.com/login"
    USERNAME = "your_username"
    PASSWORD = "your_password"
    USERNAME_SELECTOR = "#username"
    PASSWORD_SELECTOR = "#password"
    SUBMIT_SELECTOR = "button[type='submit']"

    # 视频列表（关键配置）
    VIDEO_LIST_URL = "https://your-school.com/course/123"
    VIDEO_LI_SELECTOR = "li.video-item"  # 包含视频的li
    EXCLUDE_CLASS = "decoration"  # 需要排除的li的class

    # 视频播放
    VIDEO_ELEMENT_SELECTOR = "video"
    PLAY_BUTTON_SELECTOR = None
    DEFAULT_WAIT_TIME = 60

    # 浏览器
    HEADLESS = False

    # ========== 不需要修改下面的代码 ==========
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

## ❓ 常见问题

### Q1: 找不到视频链接？

**A:** 检查以下几点：
1. 选择器是否正确？运行 `debug_page.py` 查看
2. 页面是否完全加载？增加等待时间
3. 是否需要登录才能看到视频？先确保登录成功
4. 在浏览器Console测试选择器：`document.querySelectorAll('你的选择器')`

### Q2: 提取了错误的链接？

**A:**
1. 检查是否有装饰性li需要排除，使用 `EXCLUDE_CLASS` 参数
2. 使用更精确的选择器，如 `li.video-item` 而不是 `li`
3. 在浏览器中手动检查li的class名称

### Q3: 提取了重复的链接？

**A:** 脚本已自动去重，如果仍有重复：
1. 检查是否有多个 `<a>` 标签指向同一个URL
2. 手动过滤：`video_links = list(dict.fromkeys(video_links))`

### Q4: 提取的链接数量不对？

**A:**
1. 运行调试脚本查看实际的 `<a>` 标签数量
2. 检查是否有隐藏的链接
3. 确认是否正确排除了装饰性li
4. 在Console中测试：`document.querySelectorAll('li.video-item a').length`

### Q5: 需要特定顺序观看视频？

**A:** 链接会按照页面上的顺序提取。如果需要调整：
```python
video_links = await automation.get_nested_video_links(...)
video_links.reverse()  # 反转顺序
# 或
video_links.sort()  # 排序
```

## 🎉 总结

使用步骤：
1. ✅ 运行 `debug_page.py` 分析页面结构
2. ✅ 找到正确的 CSS 选择器
3. ✅ 配置 `scripts.py` 中的选择器
4. ✅ 运行 `scripts.py` 开始自动观看

现在就试试吧！如有问题，查看调试输出或在浏览器Console中测试选择器。🚀
