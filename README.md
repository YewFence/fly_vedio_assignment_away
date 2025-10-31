# 视频自动观看脚本 - 华南师范大学Moodle版

使用 Playwright 自动登录华南师范大学Moodle系统、点击视频链接并等待视频播放完成。

## 功能特点

- ✅ Cookie登录（无需配置复杂的用户名密码）
- ✅ **URL模式自动匹配视频链接**（超简单！）
- ✅ 自动播放视频并等待播放完成
- ✅ 智能检测视频时长
- ✅ 显示进度条和实时状态
- ✅ 支持有头/无头模式运行
- ✅ 专为华南师范大学Moodle系统优化

## 📚 快速导航

- **获取Cookie**: [HOW_TO_GET_COOKIES.md](HOW_TO_GET_COOKIES.md) ⭐ 必读
- **Cookie详细指南**: [COOKIE_GUIDE.md](COOKIE_GUIDE.md)
- **更新日志**: [CHANGELOG.md](CHANGELOG.md)

## 安装步骤

本项目已使用 `uv` 管理依赖,Playwright 和浏览器已安装完成。

---

## 🚀 快速开始（3步完成！）

### 第一步：获取Cookie

本脚本使用Cookie登录，无需配置用户名密码。

**最简单的方法**：

1. 安装浏览器扩展 [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
2. 在浏览器中登录 Moodle (https://moodle.scnu.edu.cn)
3. 点击扩展图标 → Export → JSON
4. 保存为 `cookies.json` 到 `school_vedio_hw` 目录

**详细说明**: [HOW_TO_GET_COOKIES.md](HOW_TO_GET_COOKIES.md) ⭐

### 第二步：配置脚本

从示例文件复制一份配置：

```bash
# Windows
copy config_example.py config.py

# Linux/Mac
cp config_example.py config.py
```

编辑 `config.py` 文件：

```python
# Cookie登录
BASE_URL = "https://moodle.scnu.edu.cn"
COOKIE_FILE = "cookies.json"

# 视频列表（重要！填写你的课程链接）
VIDEO_LIST_URL = "https://moodle.scnu.edu.cn/course/view.php?id=12345"  # 改成你的课程链接

# URL模式（通常不需要修改）
URL_PATTERN = "https://moodle.scnu.edu.cn/mod/fsresource/view.php?id="

# 视频播放
VIDEO_ELEMENT_SELECTOR = "video"
PLAY_BUTTON_SELECTOR = None
DEFAULT_WAIT_TIME = 60

# 浏览器
HEADLESS = False
```

**如何找到课程链接？**
1. 登录Moodle
2. 进入你的课程页面
3. 查看浏览器地址栏：`https://moodle.scnu.edu.cn/course/view.php?id=12345`
4. `12345` 就是课程ID

**什么是URL模式？**
- 脚本会自动在课程页面中查找所有包含此模式的链接
- 默认值 `"https://moodle.scnu.edu.cn/mod/fsresource/view.php?id="` 适用于Moodle的资源类型视频
- 无需配置选择器，脚本自动匹配！

### 第三步：运行脚本

```bash
cd school_vedio_hw
uv run python scripts.py
```

---

## 📖 工作原理

脚本使用URL模式匹配，自动查找页面中所有符合模式的视频链接：

```
1. 登录Moodle（使用Cookie）
   ↓
2. 访问课程页面
   ↓
3. 自动查找所有包含URL模式的链接
   例如: https://moodle.scnu.edu.cn/mod/fsresource/view.php?id=123456
   ↓
4. 依次访问每个视频链接
   ↓
5. 自动播放并等待视频完成
   ↓
完成！
```

**无需配置复杂的CSS选择器！** 只需要知道视频链接的URL格式即可！

---

## 🔧 配置说明

### 必须配置的项

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `VIDEO_LIST_URL` | 课程页面URL | `https://moodle.scnu.edu.cn/course/view.php?id=12345` |
| `cookies.json` | Cookie文件 | 使用扩展导出 |

### 通常不需要修改的项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `URL_PATTERN` | 视频链接模式 | `.../mod/fsresource/view.php?id=` |
| `VIDEO_ELEMENT_SELECTOR` | 视频标签 | `video` |

### 可选配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `PLAY_BUTTON_SELECTOR` | 播放按钮选择器 | `None`（自动播放）|
| `DEFAULT_WAIT_TIME` | 默认等待时间（秒） | `60` |
| `HEADLESS` | 是否显示浏览器 | `False`（显示）|

---

## 💡 常见问题

### Q: 如何找到课程URL？

**A**:
1. 在浏览器中访问课程页面
2. 右键点击任意视频链接 → 复制链接地址
3. 链接格式通常是: `https://moodle.scnu.edu.cn/mod/fsresource/view.php?id=123456`
4. 固定部分就是URL模式（不包括最后的数字）


---

## ⚙️ 高级用法

### 无头模式（后台运行）

```python
HEADLESS = True
```

### 调整等待时间

如果视频较长，可以增加默认等待时间：

```python
DEFAULT_WAIT_TIME = 120  # 等待120秒（2分钟）
```


---

## 📂 项目文件结构

```
school_vedio_hw/
├── scripts.py              # 主脚本（已优化）✅
├── config.py               # 配置文件
├── config_example.py       # 配置示例
├── cookies.json            # Cookie文件 ⭐ 必需
│
├── README.md               # 本文档
├── HOW_TO_GET_COOKIES.md   # Cookie获取指南 ⭐
├── COOKIE_GUIDE.md         # Cookie详细指南
├── CHANGELOG.md            # 更新日志
│
├── .gitignore              # Git忽略文件
└── pyproject.toml          # 项目依赖
```

---

## 🔒 安全注意事项

- ✅ `config.py` 和 `cookies.json` 已添加到 `.gitignore`
- ⚠️ 不要分享Cookie文件
- ⚠️ 不要上传配置文件到公开平台
- ⚠️ Cookie会过期，定期更新

---

## 📝 版本信息

**当前版本**: 2.0 - URL模式匹配版

**主要特点**:
- 使用URL模式自动匹配视频链接
- 移除了复杂的CSS选择器配置
- 更简单、更可靠

查看完整更新日志: [CHANGELOG.md](CHANGELOG.md)

---

## 🎉 总结

使用URL模式匹配，配置超简单：

1. ✅ 导出Cookie到 `cookies.json`
2. ✅ 填写课程ID到 `VIDEO_LIST_URL`
3. ✅ 运行 `uv run python scripts.py`

**无需配置复杂的CSS选择器！**

需要帮助？查看 [HOW_TO_GET_COOKIES.md](HOW_TO_GET_COOKIES.md) 或相关文档！🚀
