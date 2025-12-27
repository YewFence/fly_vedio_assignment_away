# 如何获取Cookie

## 方法一：使用浏览器扩展（推荐）⭐

### Chrome/Edge

1. 安装扩展：
   - [Cookie-Editor](https://microsoftedge.microsoft.com/addons/detail/cookieeditor/neaplmfkghagebokkhpjpoebhdledlfi) （推荐）

2. 在浏览器中**登录你的目标网站**

3. 点击浏览器工具栏中的扩展图标

4. 选择 "Export" → "JSON"

此时 Cookies 就已经保存在你的剪贴板中了

### Firefox

1. 安装 [Cookie Quick Manager](https://addons.mozilla.org/zh-CN/firefox/addon/cookie-quick-manager/)

2. 在浏览器中**登录你的目标网站**

3. 点击扩展图标 → Export → JSON

此时 Cookies 就已经保存在你的剪贴板中了

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

### Q: Cookie安全吗？

A: Cookie包含你的登录凭证，请注意：
- ✅ 不要分享Cookie文件
- ✅ 不要上传到公开平台

### Q: 如何判断Cookie已过期？

A: 运行脚本时如果提示"登录失败"，说明Cookie可能已过期，需要重新获取。
