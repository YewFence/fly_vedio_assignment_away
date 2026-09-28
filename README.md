# FlyVideoAssignmentAway

[![Release](https://img.shields.io/github/v/release/YewFence/fly_video_assignment_away?sort=semver)](https://github.com/YewFence/fly_video_assignment_away/releases)
[![License](https://img.shields.io/github/license/YewFence/fly_video_assignment_away)](LICENSE)

> SCNU 砺儒云 (Moodle) 视频自动观看工具

基于 Playwright 的自动化脚本，支持自动登录华南师范大学砺儒云系统、解析视频列表并完成自动播放。

## ✨ 功能特点

- ✅ **多种登录方式**: 支持账号密码自动登录（推荐）及手动 Cookie 登录
- ✅ **状态自动维护**: 自动检测并刷新登录状态
- ✅ **智能链接解析**: 自动匹配并提取课程中的视频链接
- ✅ **精准播放控制**: 实时检测播放进度，确保视频真正播放完成
- ✅ **断点续播**: 自动处理播放中断，确保流程不间断
- ✅ **可视化进度**: 基于 `rich` 库构建的美化进度条，实时展示剩余时长
- ✅ **多模式支持**: 支持有界面窗口模式或后台无头模式运行
- ✅ **交互式配置引导**: 首次运行自动启动配置向导，无需手动创建 `.env` 文件
- ✅ **专为 SCNU 优化**: 深度适配华南师范大学 Moodle 平台

---

## 🚀 快速开始

### 前置要求

本程序依赖系统中已安装的浏览器，请确保您的电脑上安装了以下任一浏览器：
- **Microsoft Edge** (推荐，已通过完整测试)
- **Google Chrome**

> 理论上 Playwright 支持 Firefox / Safari(Webkit) ，但是这俩用的人都不多，我就懒了，但是也欢迎提交 [PR](https://github.com/YewFence/fly_video_assignment_away/pulls)

> 💡 **提示**: 目前主要在 Edge 浏览器上进行开发和测试。若在其他浏览器中遇到异常，欢迎[提交反馈](#-反馈与建议)。
> 
> 本程序已经在 Mac 平台（Chrome 浏览器）上以[从源码运行](#️-从源码运行)的方式测试过，工作正常，非常感谢帮我测试的同学！但我没有 Mac 设备，无法持续测试 macOS 可执行文件，因此暂时无法保证它始终正常工作。

### 第一步：下载程序

前往 [Releases](https://github.com/YewFence/fly_video_assignment_away/releases) 页面，下载对应系统的可执行文件：
- **Windows**: `fly_video_assignment_away-windows.exe`
- **macOS**: `fly_video_assignment_away-macos`

> ⚠️ **重要提示**: 目前生成的可执行文件发行版（Release）**尚未经过充分测试**，可能存在运行不稳定的情况。
> 
> 若您在运行过程中遇到严重问题，建议：
> 1. 跟随指引[从源码运行](#️-从源码运行)，源码已经经过端到端测试
> 2. 欢迎[提交反馈](#-反馈与建议)报告问题，我会~~尽快~~找时间进行修复。


### 第二步：启动并完成配置

直接双击运行程序。**首次运行时，程序会自动启动配置向导**，引导您完成以下配置：

1. **浏览器类型**: 选择 `msedge` 或 `chrome`（默认 msedge）
2. **无头模式**: 选择是否隐藏浏览器窗口（默认否，推荐新手显示窗口）
3. **课程链接**: 输入您需要观看视频的课程页面 URL

**如何获取课程链接？**
1. 登录 [砺儒云系统](https://moodle.scnu.edu.cn/)。
2. 点击进入您需要观看视频的课程页面。
3. 复制浏览器地址栏中的完整 URL（类似于 `https://moodle.scnu.edu.cn/course/view.php?id=XXXXX`）。

配置完成后，程序会在当前目录创建 `.env` 文件，下次启动时直接使用。如需修改配置，可以直接编辑 `.env`（格式参考 [.env.example](./.env.example)），或删除它后重新运行程序以再次触发配置向导。

### 第三步：登录并自动播放

如果未开启无头模式，程序会自动打开一个浏览器窗口，最小化即可。整个流程全自动完成，请不要手动操作该窗口，也不要关闭浏览器或结束进程，否则程序会直接终止。

如果已有保存的 Cookie 会自动尝试登录；否则推荐选择「账号密码登录」，在命令行中输入账号密码即可自动完成 SSO 登录，程序随后会自动接管播放流程。

> 请注意：短时间登录错误次数过多账户会被锁定一个小时
> 手动端到端测试登录代码的弊端出现了😢

---

## 🛠️ 从源码运行

如果您熟悉 Python 环境，也可以直接运行源代码：

### 环境要求
- **Python**: 3.13+
- **venv 管理**: 推荐使用 [uv](https://github.com/astral-sh/uv)

### 快速开始 (uv，推荐)
```bash
# 1. 克隆仓库
git clone https://github.com/YewFence/fly_video_assignment_away.git
cd fly_video_assignment_away

# 2. 安装依赖
uv sync

# 3. 运行（首次运行会自动启动配置向导）
uv run fly-video-assignment-away
```

### 快速开始 (pip + venv)

如果你不想安装 uv，也可以用 Python 自带的 venv + pip：

```bash
# 1. 克隆仓库
git clone https://github.com/YewFence/fly_video_assignment_away.git
cd fly_video_assignment_away

# 2. 创建并激活虚拟环境
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. 安装依赖
pip install .

# 4. 运行（首次运行会自动启动配置向导）
fly-video-assignment-away
```

---

## ⚙️ 工作流程

```mermaid
graph TD
    A[启动程序] --> B{存在已保存的 Cookie?}
    B -- 是 --> C[自动尝试 Cookie 登录]
    C --> D{登录成功?}
    D -- 是 --> F[访问指定的课程页面]
    D -- 否 --> E[选择登录方式]
    B -- 否 --> E
    E --> F
    F --> G[扫描并解析视频资源链接]
    G --> H[依次进入视频页面播放]
    H --> I{是否检测到完成?}
    I -- 否 --> H
    I -- 是 --> J[检查下一个视频]
    J -- 全部完成 --> K[退出程序]
```

---

## 🔐 获取登录凭证

### 1. 账号密码登录 (推荐)
启动程序后，选择 `账号密码登录` 模式，在命令行中输入账号和密码。程序会自动完成 SSO 登录并获取砺儒云的会话 Cookie，全程无需手动操作浏览器。登录成功后 Cookie 会自动保存，下次启动时会优先尝试复用。

### 2. 手动获取 Cookies 登录
1. 安装 [Cookie-Editor](https://microsoftedge.microsoft.com/addons/detail/cookieeditor/neaplmfkghagebokkhpjpoebhdledlfi) 扩展。
2. 在浏览器中登录 [SCNU 砺儒云](https://moodle.scnu.edu.cn/)。
3. 点击插件，选择 "Export" 将 Cookies 导出为 **JSON** 格式。
4. 运行程序，选择 `使用您手动获取的 Cookies 登录` 模式，将导出的内容粘贴进程序中。

> [详细 Cookie 获取指南](docs/how_to_get_cookie.md)

---

## ⚠️ 安全与规范

- **隐私保护**: 请妥善保管您的 `.env` 和 `cookies.json` 文件，切勿分享给他人或上传至公开平台。
- **定期更新**: Cookie 具有时效性，若登录失效请重新运行程序使用账号密码登录。
- **合理使用**: 本工具仅用于辅助学习，请确保您的使用行为符合学校相关规定。

---

## ❓ 常见问题 (FAQ)

**Q: 为什么不需要单独下载浏览器驱动？**
A: 本项目基于 Playwright，默认会尝试调用系统中已安装的浏览器，无需手动管理 WebDriver。

**Q: 首次运行需要手动创建 .env 文件吗？**
A: 不需要。程序会在首次运行时启动配置向导并自动创建 `.env`，也就避免了 Windows 上手动创建时误存成 `.env.txt` 的问题。如果已经在 shell 或 CI 中设置了 `VIDEO_LIST_URL` 环境变量，向导会直接跳过。

**Q: 重新运行配置向导会覆盖我的其他配置吗？**
A: 不会。向导只更新 `BROWSER`、`HEADLESS`、`VIDEO_LIST_URL` 三项，保留其他键和注释，并在写入前把原文件备份为 `.env.bak`。

**Q: macOS 或 Linux 用户如何配置？**
A: 配置向导在所有平台上都可用。如需手动修改，可以把 `.env` 中的 `BROWSER` 改为 `msedge` 或 `chrome`，并确保系统中已安装相应浏览器。

**Q: 浏览器是 Flatpak 等非标准方式安装的，程序找不到怎么办？**
A: 可以通过 `.env` 或同名环境变量手动指定浏览器，这些是高级配置，配置向导不会询问。

推荐做法是用 `BROWSER_EXECUTABLE_PATH` 指定浏览器的可执行文件，程序会照常自行启动和关闭浏览器，`HEADLESS` 和静音也照常生效。Flatpak 会为每个应用导出一个启动脚本，可以直接填这个路径（用户级安装在 `~/.local/share/flatpak/exports/bin/` 下）：

```env
BROWSER_EXECUTABLE_PATH=/var/lib/flatpak/exports/bin/com.microsoft.Edge
```

设置后 `BROWSER` 会被忽略。即使您已经开着同一个浏览器，程序也会使用独立的临时配置启动一个新实例，不会影响已打开的窗口。

备选做法是自己启动浏览器并开启远程调试端口，再用 `CDP_ENDPOINT` 让程序连接它：

```bash
# 1. 启动浏览器（以 Flatpak 版 Edge 为例，必须使用独立的配置目录，否则调试端口会被已打开的实例忽略）
flatpak run com.microsoft.Edge \
  --remote-debugging-address=127.0.0.1 \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.var/app/com.microsoft.Edge/fly-video-profile" \
  --mute-audio

# 2. 在 .env 中加入
CDP_ENDPOINT=http://127.0.0.1:9222
```

`CDP_ENDPOINT` 优先级最高，设置后 `BROWSER`、`HEADLESS` 和 `BROWSER_EXECUTABLE_PATH` 都会被忽略，静音等启动参数也需要像上面一样自己加。程序退出时只会断开连接，不会关闭您的浏览器。请注意：调试端口开启期间，本机任何进程都可以完全控制该浏览器，用完请及时关闭。

**Q: 登录状态失效怎么办？**
A: 如果 Cookie 过期，最简单的方法是重新运行程序并选择账号密码登录。

---

## 🧰 开发

项目使用 mise 统一管理工具链和可复用任务：

```bash
mise trust
mise install
mise run hooks:install
mise run check
```

完整开发流程参见 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 🚀 反馈与建议
如果您在使用过程中遇到任何问题或有改进建议，欢迎提交 [Issue](https://github.com/YewFence/fly_video_assignment_away/issues)。

## 📄 开源协议
本项目基于 [MIT License](LICENSE) 协议开源。

感谢支持！
