# 如何获取Cookie

本脚本使用Cookie进行登录，无需配置用户名密码。以下是获取Cookie的方法：

## 方法一：使用浏览器扩展（推荐）⭐

### Chrome/Edge

1. 安装扩展：
   - [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) （推荐）
   - [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)

2. 在浏览器中**登录你的目标网站**

3. 点击浏览器工具栏中的扩展图标

4. 选择 "Export" → "JSON"

5. 保存为 `cookies.json` 到 `school_vedio_hw` 目录

### Firefox

1. 安装 [Cookie Quick Manager](https://addons.mozilla.org/zh-CN/firefox/addon/cookie-quick-manager/)

2. 在浏览器中**登录你的目标网站**

3. 点击扩展图标 → Export → JSON

4. 保存为 `cookies.json`

---

## 方法二：使用开发者工具

### 步骤1：登录网站

在浏览器中正常登录你的目标网站

### 步骤2：打开开发者工具

按 `F12` 打开开发者工具

### 步骤3：查看Cookie

- **Chrome/Edge**: `Application` → `Cookies` → 选择你的网站
- **Firefox**: `Storage` → `Cookies` → 选择你的网站

### 步骤4：导出Cookie

你需要将Cookie转换为JSON格式。

#### 快速方法（在Console中运行）

1. 切换到 `Console` 标签

2. 粘贴并运行以下代码：

```javascript
// 获取当前网站的所有Cookie
const cookies = document.cookie.split(';').map(item => {
  const [name, value] = item.split('=').map(s => s.trim());
  return {
    name: name,
    value: value,
    domain: window.location.hostname,
    path: '/',
    expires: -1,
    httpOnly: false,
    secure: window.location.protocol === 'https:',
    sameSite: 'Lax'
  };
});

// 输出JSON格式
console.log(JSON.stringify(cookies, null, 2));
```

3. 复制输出的JSON内容

4. 创建 `cookies.json` 文件并粘贴内容

---

## 方法三：手动创建Cookie文件

如果你知道关键的Cookie（如 session_id、token 等），可以手动创建：

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

**注意**：
- `name`: Cookie的名称
- `value`: Cookie的值（最重要！）
- `domain`: 网站域名（加点号表示包括所有子域名）
- `expires`: 过期时间（-1表示会话Cookie）

---

## 验证Cookie是否有效

创建 `cookies.json` 后，运行脚本测试：

```bash
cd school_vedio_hw
uv run python scripts.py
```

如果看到：
- ✅ `✓ Cookie已从文件加载`
- ✅ `✓ Cookie登录成功`

说明Cookie有效！

如果看到：
- ❌ `Cookie加载失败`

检查：
1. 文件名是否为 `cookies.json`
2. 文件是否在 `school_vedio_hw` 目录下
3. JSON格式是否正确
4. Cookie是否已过期

---

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
    "expires": -1,
    "httpOnly": false,
    "secure": true,
    "sameSite": "Strict"
  }
]
```

---

## 常见问题

### Q: Cookie多久会过期？

A: 取决于网站设置，一般：
- 学校网站：3-7天
- 视频网站：30-90天
- 金融网站：15-30分钟

Cookie过期后需要重新获取。

### Q: Cookie安全吗？

A: Cookie包含你的登录凭证，请注意：
- ✅ 不要分享Cookie文件
- ✅ 不要上传到公开平台
- ✅ 定期更新Cookie
- ✅ 使用后可以删除

### Q: 如何判断Cookie已过期？

A: 运行脚本时如果提示"登录失败"，说明Cookie可能已过期，需要重新获取。

### Q: 可以在多台电脑上用同一个Cookie吗？

A: 部分网站允许，但有些网站会检测IP或设备，可能导致Cookie失效。

---

## 文件位置

确保 `cookies.json` 文件放在正确的位置：

```
school_vedio_hw/
├── scripts.py
├── config.py
├── cookies.json          ← Cookie文件放这里
└── ...
```

---

## 需要帮助？

查看完整的Cookie指南：[COOKIE_GUIDE.md](COOKIE_GUIDE.md)

---

## 快速开始

1. ✅ 在浏览器中登录网站
2. ✅ 使用扩展导出Cookie为 `cookies.json`
3. ✅ 将文件放到 `school_vedio_hw` 目录
4. ✅ 运行 `uv run python scripts.py`

就这么简单！🚀
