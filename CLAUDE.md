# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

FlyVedioAssignmentAway —— 华南师范大学砺儒云 (Moodle) 视频自动观看工具。基于 Playwright (async API) 自动登录、解析课程视频列表并完成批量播放。

## 开发命令

```bash
# 安装依赖
uv sync

# 运行程序（两种方式）
uv run python main.py                    # 通过入口脚本
uv run python -m fly_video_assignment_away  # 通过包模块

# 构建可执行文件 (CI 使用)
uv add pyinstaller
uv run pyinstaller --onefile --name fly_video_assignment_away main.py
```

Python 版本要求: **3.13+**，使用 uv 管理依赖，无 lint/test 配置。

## 架构

项目采用 **Manager 三层架构** + **包结构**，入口为 `main.py`，核心逻辑在 `fly_video_assignment_away/` 包中：

```text
main.py                                  # 入口脚本（向后兼容）

fly_video_assignment_away/               # 主包
├── __init__.py                          # 包初始化
├── __main__.py                          # 主入口：欢迎界面 → 登录流程 → 视频播放流程
├── config.py                            # 配置中心：从 .env 读取敏感配置 + 硬编码的平台常量
├── logger.py                            # 日志系统：RichHandler (终端美化) + RotatingFileHandler (log/debug.log)
├── automation/                          # 自动化核心逻辑
│   ├── __init__.py
│   ├── browser.py                       # BrowserManager - 浏览器生命周期管理 (Chromium channel 模式)
│   ├── auth.py                          # AuthManager - 登录认证 (Cookie 登录 / 账号密码 SSO 登录)
│   ├── video.py                         # VideoManager - 视频链接提取、播放控制、进度监控 (rich 进度条)
│   └── exception_context.py             # 异常处理装饰器 + BrowserClosedError 自定义异常
└── cli/                                 # CLI 工具包
    ├── __init__.py
    ├── cookie_fix.py                    # Cookie 转换工具：将浏览器导出的 Cookie JSON 转换为 Playwright 格式
    └── setup_wizard.py                  # 配置向导：首次运行交互式配置
```

### 核心流程

1. `BrowserManager.setup()` 启动 Playwright Chromium (channel 模式，使用系统安装的浏览器)
2. `AuthManager` 尝试 Cookie 登录，失败则走账号密码 SSO 登录 → 跳转砺儒云获取 Moodle Cookie
3. `VideoManager.get_video_links_by_pattern()` 通过 URL 模式匹配从课程页提取视频链接
4. `VideoManager.watch_videos()` 批量播放，每个视频循环检测播放状态 + 平台完成标记

### 关键模式

- **全异步**：所有浏览器操作使用 `playwright.async_api`，入口通过 `asyncio.run()` 驱动
- **`@exception_context` 装饰器**：统一包装异常，自动识别浏览器关闭场景并转为 `BrowserClosedError`
- **Cookie 会话维护**：播放过程中自动检测"延长会话"按钮并刷新 Cookie，防止超时

## 配置

环境变量通过 `.env` 文件配置（参考 `.env.example`）：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `BROWSER` | 浏览器类型 | `msedge` |
| `HEADLESS` | 无头模式 | `false` |
| `VIDEO_LIST_URL` | 课程页面 URL（必填） | 无 |

平台相关常量（SSO URL、CSS 选择器等）硬编码在 `fly_video_assignment_away/config.py` 中。

## CI/CD

- **PR Build Test** (`.github/workflows/pr-build.yml`): PR 到 main 时触发，Windows + macOS 双平台构建验证
- **Build Executables** (`.github/workflows/build.yml`): 推送 `v*` tag 时触发，PyInstaller 打包并创建 GitHub Release
