# 🚀 快速使用指南

## 3步开始使用

### 1. 获取Cookie

安装扩展 → 登录Moodle → 导出Cookie

- 安装 [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
- 登录 https://moodle.scnu.edu.cn
- 点击扩展 → Export → JSON
- 保存为 `cookies.json`

### 2. 配置课程

```bash
copy config_example.py config.py
```

编辑 `config.py`：

```python
VIDEO_LIST_URL = "https://moodle.scnu.edu.cn/course/view.php?id=你的课程ID"
```

**如何找到课程ID？**
- 进入课程页面
- 查看地址栏：`...course/view.php?id=12345`
- `12345` 就是课程ID

### 3. 运行

```bash
uv run python scripts.py
```

---

## 就这么简单！

✅ **无需配置复杂的CSS选择器**
✅ **无需配置用户名密码**
✅ **自动匹配所有视频链接**

脚本会自动：
1. 使用Cookie登录
2. 访问课程页面
3. 查找所有视频链接（格式：`.../mod/fsresource/view.php?id=数字`）
4. 依次播放每个视频
5. 等待视频播放完成

---

## 常见问题

### Cookie过期了？
重新导出一次即可，3-7天过期一次。

### 找不到视频？
检查：
1. Cookie是否有效（重新导出试试）
2. 课程ID是否正确
3. 视频链接格式是否匹配（查看 `config.py` 中的 `URL_PATTERN`）

### 其他问题？
查看 [README.md](README.md) 完整文档

---

## 配置说明

只需要配置2个东西：

### 1. Cookie文件
`cookies.json` - 从浏览器扩展导出

### 2. 课程ID
`VIDEO_LIST_URL` - 课程页面URL

其他配置通常不需要修改！

---

## URL模式说明

脚本使用URL模式自动匹配视频链接。

**默认模式**：
```python
URL_PATTERN = "https://moodle.scnu.edu.cn/mod/fsresource/view.php?id="
```

这会匹配所有类似这样的链接：
- `https://moodle.scnu.edu.cn/mod/fsresource/view.php?id=123456`
- `https://moodle.scnu.edu.cn/mod/fsresource/view.php?id=789012`

**如何验证？**
1. 在浏览器中访问课程页面
2. 右键点击视频链接 → 复制链接地址
3. 查看链接格式是否包含 URL_PATTERN

**其他常见模式**：
```python
# 资源文件
URL_PATTERN = "https://moodle.scnu.edu.cn/mod/resource/view.php?id="

# 页面
URL_PATTERN = "https://moodle.scnu.edu.cn/mod/page/view.php?id="
```

---

## 完整配置示例

```python
# config.py

# Cookie登录
COOKIE_FILE = "cookies.json"
BASE_URL = "https://moodle.scnu.edu.cn"

# 视频列表（改成你的课程ID）
VIDEO_LIST_URL = "https://moodle.scnu.edu.cn/course/view.php?id=12345"

# URL模式（通常不需要修改）
URL_PATTERN = "https://moodle.scnu.edu.cn/mod/fsresource/view.php?id="

# 视频播放（通常不需要修改）
VIDEO_ELEMENT_SELECTOR = "video"
PLAY_BUTTON_SELECTOR = None
DEFAULT_WAIT_TIME = 60

# 浏览器（False=显示窗口，True=后台运行）
HEADLESS = False
```

---

## 运行示例

```bash
$ uv run python scripts.py

正在加载配置...
✓ 浏览器启动成功
正在使用Cookie登录...
✓ Cookie已从文件加载: cookies.json
✓ Cookie登录成功,当前页面: https://moodle.scnu.edu.cn

正在提取视频链接...
URL模式: https://moodle.scnu.edu.cn/mod/fsresource/view.php?id=

正在访问视频列表页面: https://moodle.scnu.edu.cn/course/view.php?id=12345
✓ 找到 15 个匹配的视频链接

示例链接:
  1. https://moodle.scnu.edu.cn/mod/fsresource/view.php?id=123456
  2. https://moodle.scnu.edu.cn/mod/fsresource/view.php?id=123457
  3. https://moodle.scnu.edu.cn/mod/fsresource/view.php?id=123458
  4. https://moodle.scnu.edu.cn/mod/fsresource/view.php?id=123459
  5. https://moodle.scnu.edu.cn/mod/fsresource/view.php?id=123460
  ... 还有 10 个链接

开始观看 15 个视频

[1/15] 当前视频:
============================================================
正在访问视频页面: https://moodle.scnu.edu.cn/mod/fsresource/view.php?id=123456
✓ 视频时长: 300.0 秒 (5.0 分钟)
⏳ 等待视频播放完成(预计 305.0 秒)...
   已等待 10/305 秒 (3%)
   已等待 20/305 秒 (7%)
   ...
✓ 视频播放完成

[2/15] 当前视频:
...
```

---

## 需要帮助？

- Cookie获取：[HOW_TO_GET_COOKIES.md](HOW_TO_GET_COOKIES.md)
- 完整文档：[README.md](README.md)
- 更新日志：[CHANGELOG.md](CHANGELOG.md)

---

**版本**: 2.0 - URL模式匹配版
**特点**: 超简单配置，自动匹配视频链接，无需CSS选择器！
