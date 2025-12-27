# FlyVedioAssignmentAway!
> SCNU 砺儒云 (Moodle) 视频自动观看工具

基于 Playwright 的自动化脚本，支持自动登录华南师范大学砺儒云系统、解析视频列表并完成自动播放。

## ✨ 功能特点

- ✅ **多种登录方式**: 支持 Cookie 登录及交互式手动登录
- ✅ **状态自动维护**: 自动检测并刷新登录状态
- ✅ **智能链接解析**: 自动匹配并提取课程中的视频链接
- ✅ **精准播放控制**: 实时检测播放进度，确保视频真正播放完成
- ✅ **断点续播**: 自动处理播放中断，确保流程不间断
- ✅ **可视化进度**: 基于 `rich` 库构建的美化进度条，实时展示剩余时长
- ✅ **多模式支持**: 支持有界面窗口模式或后台无头模式运行
- ✅ **专为 SCNU 优化**: 深度适配华南师范大学 Moodle 平台

---

## 🚀 快速开始（推荐）

### 前置要求

本程序依赖系统中已安装的浏览器，请确保您的电脑上安装了以下任一浏览器：
- **Microsoft Edge** (推荐，已通过完整测试)
- **Google Chrome**
- **Mozilla Firefox**
- **Safari**

> 💡 **提示**: 目前主要在 Edge 浏览器上进行开发和测试。若在其他浏览器中遇到异常，欢迎[提交 Issue](#反馈与建议) 反馈。
> 
> **另外...** 本程序目前从未在 Mac 平台进行过测试（作者手中暂无 Mac 设备），非常欢迎有条件的好心人帮忙测试运行效果，并在 [Issue](#反馈与建议) 中反馈！

### 第一步：下载程序

前往 [Releases](https://github.com/YewFence/fly_vedio_assignment_away/releases) 页面，下载对应系统的可执行文件：
- **Windows**: `school-video-hw-windows.exe`
- **macOS**: `school-video-hw-macos`

> ⚠️ **重要提示**: 目前生成的可执行文件发行版（Release）**尚未经过充分测试**，可能存在运行不稳定的情况。
> 
> 若您在运行过程中遇到严重问题，建议：
> 1. 前往 Tags 下载 [v1.0.0 版本的源码](https://github.com/YewFence/fly_vedio_assignment_away/releases/tag/v1.0.0)。
> 2. 参考该版本内的 `README.md` 进行环境配置与手动运行。
> 3. 欢迎[提交 Issue](#反馈与建议) 报告问题，我会尽快进行修复。

### 第二步：创建配置文件

在程序所在目录下参考 [.env.example](./.env.example) 创建 `.env` 配置文件：

```env
# 浏览器类型 (msedge/chrome/firefox)
BROWSER=msedge

# 是否开启无头模式（true 表示隐藏浏览器界面，false 表示显示）
HEADLESS=false

# 课程详情页 URL
VIDEO_LIST_URL=https://moodle.scnu.edu.cn/course/view.php?id=12345
```

**如何获取课程链接？**
1. 登录 [砺儒云系统](https://moodle.scnu.edu.cn/)。
2. 点击进入您需要观看视频的课程页面。
3. 复制浏览器地址栏中的完整 URL（类似于 `https://moodle.scnu.edu.cn/course/view.php?id=XXXXX`）。

### 第三步：启动程序

直接双击运行程序。推荐选择「交互式登录」，在自动打开的浏览器窗口中完成登录操作，程序随后会自动接管播放流程。

---

## 🛠️ 开发者指南 (源码运行)

如果您熟悉 Python 环境，也可以直接运行源代码：

### 环境要求
- **Python**: 3.13+
- **工具**: 推荐使用 [uv](https://github.com/astral-sh/uv)

### 快速上手
```bash
# 1. 克隆仓库
git clone https://github.com/YewFence/fly_vedio_assignment_away.git
cd fly_vedio_assignment_away

# 2. 安装依赖
uv sync

# 3. 配置环境 (编辑 .env 文件)
cp .env.example .env

# 4. 运行
uv run python main.py
```

---

## ⚙️ 工作流程

```mermaid
graph TD
    A[启动程序并登录] --> B[访问指定的课程页面]
    B --> C[扫描并解析视频资源链接]
    C --> D[依次进入视频页面播放]
    D --> E{是否检测到完成?}
    E -- 否 --> D
    E -- 是 --> F[检查下一个视频]
    F -- 全部完成 --> G[退出程序]
```

---

## 🔐 获取登录凭证

### 1. 交互式登录 (推荐)
启动程序后，选择 `交互式登录` 模式。脚本会唤起一个浏览器窗口，您可以手动输入账号密码通过统一身份认证登录。登录完成后，脚本会自动捕获会话状态。

### 2. 手动获取 Cookies 登录
1. 安装 [Cookie-Editor](https://microsoftedge.microsoft.com/addons/detail/cookieeditor/neaplmfkghagebokkhpjpoebhdledlfi) 扩展。
2. 在浏览器中登录 [SCNU 砺儒云](https://moodle.scnu.edu.cn/)。
3. 点击插件，选择 "Export" 将 Cookies 导出为 **JSON** 格式。
4. 运行程序，选择 `使用您手动获取的 Cookies 登录` 模式然后运行程序，将导出的内容粘贴进程序中。

> [详细 Cookie 获取指南](docs/how_to_get_cookie.md)

---

## ⚠️ 安全与规范

- **隐私保护**: 请妥善保管您的 `.env` 和 `browser_cookies.json` 文件，切勿分享给他人或上传至公开平台。
- **定期更新**: Cookie 具有时效性，若登录失效请重新获取或使用交互式登录。
- **合理使用**: 本工具仅用于辅助学习，请确保您的使用行为符合学校相关规定。

---

## ❓ 常见问题 (FAQ)

**Q: 为什么不需要单独下载浏览器驱动？**
A: 本项目基于 Playwright，默认会尝试调用系统中已安装的浏览器，无需手动管理 WebDriver。

**Q: macOS 或 Linux 用户如何配置？**
A: 请在 `.env` 文件中将 `BROWSER` 修改为 `chrome` 或 `firefox`，并确保系统中已安装相应浏览器。

**Q: 登录状态失效怎么办？**
A: 如果 Cookie 过期，最简单的方法是重新运行程序并选择交互式登录。

---

## 🚀 反馈与建议
如果您在使用过程中遇到任何问题或有改进建议，请随时提交 [Issue](https://github.com/YewFence/fly_vedio_assignment_away/issues)。

## 📄 开源协议
本项目基于 [MIT License](LICENSE) 协议开源。

感谢支持！
