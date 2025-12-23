# 视频自动观看脚本 - 华南师范大学lry系统

使用 Playwright 自动登录华南师范大学lry系统、点击视频链接并等待视频播放完成。

## 功能特点

- ✅ Cookie登录/交互式登录
- ✅ 自动刷新登录状态
- ✅ URL模式自动匹配视频链接
- ✅ 自动播放视频并等待播放完成
- ✅ 智能检测剩余需要播放时长
- ✅ 基于实际播放进度判断视频完成状态
- ✅ 自动继续视频，防止意外暂停
- ✅ 使用 rich 库美化进度条，实时显示播放状态
- ✅ 时间显示格式优化（时:分:秒）
- ✅ 支持窗口模式/后台模式运行
- ✅ 专为华南师范大学lry系统优化

---

## 🚀 快速开始（推荐）

### 第一步：下载可执行文件

前往 [Releases](https://github.com/YewFence/fly_vedio_assignment_away/releases) 页面，下载对应系统的可执行文件：
- **Windows**: `school-video-hw-windows.exe`
- **macOS**: `school-video-hw-macos`

### 第二步：创建配置文件

在可执行文件同目录下参考 [env.example](./.env.example) 创建 `.env` 文件：

```env
# 浏览器类型 (msedge/chrome/firefox)
BROWSER=msedge

# 是否使用无头模式 (true/false)
HEADLESS=false

# 课程链接页面URL（改成你自己的课程链接）
VIDEO_LIST_URL=https://moodle.scnu.edu.cn/course/view.php?id=12345
```

**如何找到课程链接？**
1. 登录lry系统
2. 进入你要刷的课程页面
3. 复制浏览器地址栏的链接（类似 `https://moodle.scnu.edu.cn/course/view.php?id=12345`）

### 第三步：运行程序

双击运行可执行文件，选择「交互式登录」，在弹出的浏览器窗口中登录即可。

---

## 🐍 开发者使用方式

如果你熟悉 Python，可以直接运行源码：

### 环境要求

- **Python**: >= 3.13
- **包管理**: [uv](https://github.com/astral-sh/uv)（推荐）
- **浏览器**: Microsoft Edge（Windows 默认）/ Chrome / Firefox

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/YewFence/fly_vedio_assignment_away.git
cd fly_vedio_assignment_away

# 2. 安装依赖
uv sync

# 3. 创建配置文件
copy .env.example .env  # Windows
cp .env.example .env    # Linux/macOS

# 4. 编辑 .env 文件，填入课程链接

# 5. 运行
uv run python main.py
```

---

## 📖 工作原理

```
1. 登录Moodle（交互式登录或Cookie）
   ↓
2. 访问课程页面
   ↓
3. 自动查找所有视频链接
   ↓
4. 依次播放并等待完成
   ↓
完成！
```

---

## 🔐 登录方式

### 方式一：交互式登录（推荐）

运行程序后选择交互式登录，会打开浏览器窗口让你手动登录，登录成功后程序会自动继续。

### 方式二：Cookie 文件登录

1. 安装浏览器扩展 [Cookie-Editor](https://microsoftedge.microsoft.com/addons/detail/cookieeditor/neaplmfkghagebokkhpjpoebhdledlfi)
2. 登录 https://moodle.scnu.edu.cn/my/
3. 使用扩展导出 Cookie 为 JSON 格式
4. 保存为项目目录下的 `browser_cookies.json`

详细说明: [how_to_get_cookie.md](docs/how_to_get_cookie.md)

---

## 🔒 安全注意事项

- ⚠️ 不要分享 `.env` 文件和 Cookie 文件
- ⚠️ 不要上传配置文件到公开平台
- ⚠️ Cookie 会过期，需定期更新

---

## ❓ 常见问题

### Q: 为什么不需要安装浏览器？
**A**: 程序使用系统已安装的浏览器（默认 Edge），无需额外下载。

### Q: macOS/Linux 怎么使用？
**A**: 修改 `.env` 中的 `BROWSER=chrome` 或 `BROWSER=firefox`。

### Q: Cookie 过期/登录失败？
**A**: 重新使用交互式登录，或重新导出 Cookie。

---

需要帮助？遇到BUG？请提出 [Issue](https://github.com/YewFence/fly_vedio_assignment_away/issues) 🚀
