# 脚本化运行模式

本文档说明如何在完全无交互的脚本化模式下运行 FlyVideoAssignmentAway。

> [!NOTE]
> 本功能正在测试中

## 概述

从 v2.6.0 开始，程序支持通过环境变量配置所有选项，实现完全自动化运行，无需任何用户交互。

## 启用脚本化模式

设置环境变量 `SKIP_SETUP_WIZARD=true` 即可跳过交互式配置向导，程序将从环境变量读取所有配置。

## 必需的环境变量

### 基础配置

```bash
# 跳过配置向导（必需）
SKIP_SETUP_WIZARD=true

# 课程链接（必需）
VIDEO_LIST_URL=https://moodle.scnu.edu.cn/course/view.php?id=12345

# 浏览器配置（可选，有默认值）
BROWSER=msedge              # msedge 或 chrome，默认 msedge
HEADLESS=true               # true 或 false，默认 false，建议 CI 环境改为 false
```

### 登录配置

根据登录方式选择以下配置之一：

#### 方式 1: 使用已有 Cookie 文件

```bash
# 登录模式设置为 cookie（这是默认值，可以不设置）
LOGIN_MODE=cookie
# 指定需要使用的 cookies 文件的路径
COOKIE_FILE="/path/to/your/cookies.json"

```

#### 方式 2: 账号密码自动登录

```bash
# 登录模式
LOGIN_MODE=credential

# 账号和密码（必需）
# 密码会以明文形式存储在环境变量中，请确保运行环境的安全性。
SCNU_USERNAME=your_username
SCNU_PASSWORD=your_password
```

#### 方式 3: 手动提供 Cookie JSON

```bash
# 登录模式
LOGIN_MODE=manual

# Cookie JSON 字符串（必需，格式为 Playwright cookies 数组的 JSON）
SCNU_COOKIES_JSON='[{"name":"MoodleSession","value":"...","domain":".moodle.scnu.edu.cn","path":"/"}]'
```

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: fly-video-assignment-away

on:
  workflow_dispatch:      # 手动触发

jobs:
  watch-videos:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      
      - name: Install uv
        run: pip install uv
      
      - name: Install dependencies
        run: uv sync
      
      - name: Run video watcher
        env:
          SKIP_SETUP_WIZARD: true
          VIDEO_LIST_URL: ${{ secrets.VIDEO_LIST_URL }}
          LOGIN_MODE: credential
          SCNU_USERNAME: ${{ secrets.SCNU_USERNAME }}
          SCNU_PASSWORD: ${{ secrets.SCNU_PASSWORD }}
          BROWSER: chrome
          HEADLESS: true
        run: uv run fly-video-assignment-away
```

在 GitHub 仓库的 Settings → Secrets 中添加账户密码，然后手动触发它即可。

## 注意事项

1. **Cookie 有效期**: 使用 `LOGIN_MODE=cookie` 时，需要定期检查 Cookie 是否过期
2. **密码安全**: 使用 `LOGIN_MODE=credential` 时，确保环境变量不会被记录到日志中

