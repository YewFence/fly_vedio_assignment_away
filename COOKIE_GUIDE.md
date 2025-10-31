# Cookie 登录使用指南

## 什么是Cookie登录？

Cookie登录可以让你**无需每次输入用户名密码**，脚本会自动使用保存的Cookie进行身份验证。

## Cookie 失效时间说明

### 不同类型网站的Cookie有效期

| 网站类型 | 典型有效期 | 说明 |
|---------|-----------|------|
| 🏫 **在线教育平台** | 1-7天 | 学校网站、Coursera等 |
| 🎥 **视频网站** | 30-90天 | B站、YouTube、爱优腾 |
| 📱 **社交媒体** | 7-30天 | 微博、Twitter、Facebook |
| 🛒 **电商网站** | 7-30天 | 淘宝、京东、亚马逊 |
| 💰 **金融网站** | 15-30分钟 | 网银、支付宝（安全性高）|

### Cookie失效的常见原因

1. ⏰ **超过有效期** - 最常见，服务器设置的过期时间到了
2. 🔄 **服务器更新** - 网站系统维护或升级
3. 🔐 **修改密码** - 修改密码后通常会使所有Cookie失效
4. 📍 **IP地址变化** - 某些网站会绑定IP地址
5. 🗑️ **手动登出** - 在浏览器中退出登录

## 使用方法

### 方式一：自动获取Cookie（推荐）⭐

这是最简单的方式，脚本会自动保存Cookie供下次使用。

1. **首次运行**：使用账号密码登录
   ```python
   # 在 scripts.py 的 main() 函数中配置
   USE_COOKIE_LOGIN = False  # 第一次设为False
   USERNAME = "your_username"
   PASSWORD = "your_password"
   ```

2. **运行脚本**
   ```bash
   uv run python scripts.py
   ```
   脚本会自动登录并保存Cookie到 `cookies.json`

3. **后续运行**：启用Cookie登录
   ```python
   USE_COOKIE_LOGIN = True  # 改为True
   ```
   下次运行时会自动使用Cookie，无需输入密码！

### 方式二：从浏览器手动导出Cookie

如果你已经在浏览器中登录了，可以手动导出Cookie。

#### 步骤1: 安装浏览器扩展

**Chrome/Edge推荐**:
- [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
- [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)

**Firefox推荐**:
- [Cookie Quick Manager](https://addons.mozilla.org/zh-CN/firefox/addon/cookie-quick-manager/)

#### 步骤2: 导出Cookie

1. 在浏览器中登录目标网站
2. 点击扩展图标
3. 选择 "Export" 或 "导出"
4. 选择 JSON 格式
5. 保存为 `cookies.json` 到脚本目录

#### 步骤3: 调整格式（如果需要）

Playwright需要特定格式的Cookie。如果导出的格式不对，使用此脚本转换：

```python
# convert_cookies.py
import json

# 读取浏览器导出的Cookie
with open('browser_cookies.json', 'r') as f:
    browser_cookies = json.load(f)

# 转换为Playwright格式
playwright_cookies = []
for cookie in browser_cookies:
    playwright_cookie = {
        'name': cookie.get('name'),
        'value': cookie.get('value'),
        'domain': cookie.get('domain'),
        'path': cookie.get('path', '/'),
        'expires': cookie.get('expirationDate', -1),
        'httpOnly': cookie.get('httpOnly', False),
        'secure': cookie.get('secure', False),
        'sameSite': cookie.get('sameSite', 'Lax')
    }
    playwright_cookies.append(playwright_cookie)

# 保存
with open('cookies.json', 'w', encoding='utf-8') as f:
    json.dump(playwright_cookies, f, indent=2, ensure_ascii=False)

print("✓ Cookie转换完成!")
```

### 方式三：使用开发者工具手动复制

适合只需要少量Cookie的情况。

1. 按 `F12` 打开开发者工具
2. 切换到 `Application` 标签（Chrome）或 `Storage` 标签（Firefox）
3. 左侧展开 `Cookies` -> 选择你的网站
4. 手动复制关键Cookie（如 `session_id`, `token` 等）
5. 按照以下格式创建 `cookies.json`:

```json
[
  {
    "name": "session_id",
    "value": "你的session值",
    "domain": ".example.com",
    "path": "/",
    "expires": -1,
    "httpOnly": true,
    "secure": true,
    "sameSite": "Lax"
  }
]
```

## Cookie文件示例

一个完整的 `cookies.json` 文件看起来像这样：

```json
[
  {
    "name": "SESSID",
    "value": "abc123def456ghi789",
    "domain": ".example.com",
    "path": "/",
    "expires": 1735689600,
    "httpOnly": true,
    "secure": true,
    "sameSite": "Lax"
  },
  {
    "name": "user_token",
    "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "domain": "example.com",
    "path": "/",
    "expires": 1735689600,
    "httpOnly": false,
    "secure": true,
    "sameSite": "Strict"
  }
]
```

## 使用建议

### ✅ 推荐做法

1. **首次使用自动保存** - 最方便，让脚本自动处理
2. **定期更新Cookie** - 如果发现登录失败，重新生成Cookie
3. **保护Cookie文件** - 添加到 `.gitignore`，不要上传到网上
4. **使用HTTPS网站** - 更安全，Cookie不易被窃取

### ⚠️ 注意事项

1. **安全性**
   - Cookie文件包含你的登录凭证，**不要分享给他人**
   - 不要将Cookie上传到GitHub等公开平台
   - 定期删除不用的Cookie文件

2. **隐私性**
   - 在公共电脑上使用后，记得删除Cookie文件
   - 不要在他人电脑上保存你的Cookie

3. **有效性**
   - Cookie过期后需要重新登录
   - 如果网站检测到异常（如IP变化），可能会使Cookie失效
   - 某些网站限制同一Cookie不能在多个设备同时使用

## 验证Cookie是否有效

### 方法1：查看过期时间

```bash
uv run python -c "
import json
from datetime import datetime

with open('cookies.json', 'r') as f:
    cookies = json.load(f)

for cookie in cookies:
    name = cookie['name']
    expires = cookie.get('expires', -1)
    if expires == -1:
        print(f'{name}: 会话Cookie（关闭浏览器失效）')
    else:
        expire_time = datetime.fromtimestamp(expires)
        print(f'{name}: 过期时间 {expire_time}')
"
```

### 方法2：运行脚本测试

最直接的方法就是运行脚本，看能否成功登录！

```bash
uv run python scripts.py
```

如果看到：
- ✅ `✓ Cookie已从文件加载` - Cookie加载成功
- ✅ `✓ 使用Cookie登录成功` - Cookie有效
- ⚠️ `⚠ Cookie文件不存在` - 需要生成Cookie
- ⚠️ `使用账号密码登录` - Cookie失效，已自动切换到密码登录

## Cookie工作原理简图

```
第一次登录（生成Cookie）:
┌─────────┐                    ┌─────────┐
│  脚本    │ ──用户名+密码──>   │  服务器  │
│         │                    │         │
│         │ <──Set-Cookie──    │         │
└─────────┘                    └─────────┘
     │
     ├─ 保存到 cookies.json


后续访问（使用Cookie）:
┌─────────┐                    ┌─────────┐
│  脚本    │ ──Cookie──>        │  服务器  │
│         │                    │         │
│         │ <──验证通过──       │ ✓验证身份 │
└─────────┘                    └─────────┘
     │
     ├─ 从 cookies.json 读取
```

## 常见问题

### Q: Cookie多久会过期？

A: 取决于网站设置，一般：
- 学校网站：3-7天
- 视频网站：30-90天
- 金融网站：15-30分钟

### Q: Cookie失效后怎么办？

A: 脚本会自动使用账号密码重新登录并生成新的Cookie，无需手动操作。

### Q: 可以在多台电脑上用同一个Cookie吗？

A: 部分网站允许，但有些网站会检测IP或设备指纹，可能导致Cookie失效。

### Q: Cookie安全吗？

A: Cookie本身是安全的，但要注意：
- 不要分享Cookie文件给他人
- 使用HTTPS网站
- 定期更新Cookie
- 不要在不信任的电脑上保存Cookie

### Q: 如何删除Cookie？

A: 直接删除 `cookies.json` 文件即可：
```bash
rm cookies.json  # Linux/Mac
del cookies.json  # Windows
```

## 故障排查

### 问题1: Cookie加载失败

```
⚠ 加载Cookie失败: ...
```

**解决方法**:
1. 检查 `cookies.json` 文件格式是否正确（必须是有效的JSON）
2. 确认文件路径正确
3. 删除Cookie文件，重新用密码登录生成

### 问题2: Cookie已加载但登录失败

```
✓ Cookie已从文件加载
❌ 访问页面后仍显示未登录
```

**解决方法**:
1. Cookie已过期，删除文件重新生成
2. 网站更新了认证系统
3. IP地址变化被检测到
4. 将 `USE_COOKIE_LOGIN` 改为 `False`，用密码重新登录

### 问题3: 找不到cookies.json文件

```
⚠ Cookie文件不存在: cookies.json
```

**解决方法**:
这是正常的！第一次运行时Cookie文件不存在，脚本会自动：
1. 使用账号密码登录
2. 保存Cookie到文件
3. 下次运行就能使用Cookie了

## 总结

使用Cookie登录的优势：
- ⚡ **更快** - 无需每次输入密码
- 🔒 **更安全** - 密码不需要明文保存在脚本中
- 🤖 **更智能** - Cookie失效时自动切换到密码登录

推荐工作流程：
1. 第一次运行：用密码登录，自动保存Cookie
2. 后续运行：自动使用Cookie，快速登录
3. Cookie过期：自动重新登录并更新Cookie

现在就试试吧！🚀
