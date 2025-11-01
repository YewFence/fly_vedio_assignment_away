# 视频自动观看脚本 - 华南师范大学lry系统

使用 Playwright 自动登录华南师范大学lry系统、点击视频链接并等待视频播放完成。

## 功能特点

- ✅ Cookie登录
- ✅ **URL模式自动匹配视频链接**（超简单！）
- ✅ 自动播放视频并等待播放完成
- ✅ 智能检测剩余需要播放时长
- ✅ 显示实时状态
- ✅ 支持窗口模式/后台模式运行
- ✅ 专为华南师范大学lry系统优化

## 📋 环境要求

### 系统要求
- **操作系统**: Windows 10/11（需要系统已安装 Microsoft Edge 浏览器）
- **其他系统**: Linux/macOS 需要更改配置文件中的浏览器选项

### 依赖项

#### 1. Python 环境
- **Python 版本**: >= 3.13
- **包管理工具**: [uv](https://github.com/astral-sh/uv)（推荐）或 pip

#### 2. Python 包依赖
- `playwright >= 1.55.0` - 浏览器自动化框架

#### 3. 浏览器依赖
- **Microsoft Edge** - 脚本使用系统已安装的 Edge 浏览器（默认配置）
- **firefox/chrome** - 需要更改配置文件

### 安装步骤

#### 方法一：使用 uv（推荐）

```bash
# 1. 安装 uv（如果还没安装）
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 克隆项目
git clone <your-repo-url>
cd school_vedio_hw

# 3. uv 会自动创建虚拟环境并安装依赖
uv sync
```

#### 方法二：使用 pip

```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# 3. 安装依赖
pip install playwright>=1.55.0
```

#### 验证安装

```bash
# 检查 Python 版本
python --version  # 应显示 >= 3.13

# 检查 playwright 是否安装
uv pip list | grep playwright
# 或
pip list | grep playwright

# 检查 Edge 浏览器（Windows）
where msedge
# 应显示 Edge 浏览器的安装路径
```

---

## 使用步骤

## 🚀 快速开始（3步完成！）

### 第一步：获取Cookie

本脚本使用Cookie登录，无需配置用户名密码。

**最简单的方法**：

1. 安装浏览器扩展 [Cookie-Editor](https://microsoftedge.microsoft.com/addons/detail/cookieeditor/neaplmfkghagebokkhpjpoebhdledlfi)
2. 在浏览器中登录网站 (https://moodle.scnu.edu.cn/my/)
3. 使用扩展导出cookie为json文件
4. 保存为 `browser_cookies.json` 到项目目录

**详细说明**: [how_to_get_cookie.md](docs/how_to_get_cookie.md) ⭐

### 第二步：配置脚本

从示例文件复制一份配置：

```bash
# Windows
copy config_example.py config.py

# Linux/Mac
cp config_example.py config.py
```

编辑 `config.py` 文件，粘贴你要刷的课程链接，其他一般不需要修改

```python
VIDEO_LIST_URL = "https://moodle.scnu.edu.cn/course/view.php?id=12345"  # 改成你的课程链接
```

**如何找到课程链接？**
1. 登录lry
2. 进入你的课程页面
3. 查看浏览器地址栏，类似于：`https://moodle.scnu.edu.cn/course/view.php?id=12345` 直接复制粘贴即可

### 第三步：运行脚本

在项目根目录下运行
```bash
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

## 📂 项目文件结构

```
school_vedio_hw/
├── scripts.py              # 主脚本 ⭐
├── cookie_fix.py           # Cookie格式转换工具
├── config.py               # 配置文件 ⭐ 需要自己创建并配置课程链接
├── config_example.py       # 配置示例
├── browser_cookies.json    # 浏览器导出的原始Cookie ⭐ 需要自己导出
├── cookies.json            # 转换后的Cookie（自动生成）
├── pyproject.toml          # 项目依赖配置
├── uv.lock                 # uv 依赖锁定文件
├── .python-version         # Python 版本配置
├── .gitignore              # Git 忽略文件
├── README.md               # 本文档
└── docs/
    └── how_to_get_cookie.md   # Cookie获取指南
```

**关键文件说明**:
- ⭐ **必须配置**: `config.py`, `browser_cookies.json`
- 🤖 **自动生成**: `cookies.json`（由 cookie_fix.py 自动转换）
- 📦 **依赖管理**: `pyproject.toml`, `uv.lock`

---

## 🔒 安全注意事项

- ✅ `config.py` 和 `cookies.json` 和 `browser_cookie.json` 已添加到 `.gitignore`
- ⚠️ 不要分享Cookie文件
- ⚠️ 不要上传配置文件到公开平台
- ⚠️ Cookie会过期，定期更新

---

## ❓ 常见问题

### Q1: 项目占用多少空间？
**A**:
- Python 虚拟环境: ~200 MB
- Playwright 包: ~97 MB
- **总计**: ~300 MB

### Q2: 为什么不需要安装浏览器？
**A**: 脚本使用 `channel="msedge"` 参数调用 Windows 系统自带的 Microsoft Edge 浏览器，无需通过 Playwright 下载浏览器。

### Q3: 其他系统（Linux/macOS）怎么使用？
**A**: 需要修改 `config.py` 中的浏览器启动配置：
`BROWSER="firefox"`

### Q4: Cookie 转换失败怎么办？
**A**:
1. 确保 `browser_cookies.json` 存在且不为空
2. 检查 JSON 格式是否正确
3. 重新从浏览器导出 Cookie

### Q5: 登录失败被重定向？
**A**:
1. Cookie 可能已过期，重新获取 Cookie
2. 检查 `browser_cookies.json` 是否包含 `MoodleSession` Cookie
3. 确保在浏览器中能正常登录

---

需要帮助？遇到BUG？请提出issue 🚀
