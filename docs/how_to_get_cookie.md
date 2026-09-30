# 如何获取 Cookie

## 完整流程

### 1. 登录砺儒云

从 [https://moodle.scnu.edu.cn/login/index.php](https://moodle.scnu.edu.cn/login/index.php) 登录

### 2. 确认已登录且页面在砺儒云

能正常打开 [https://moodle.scnu.edu.cn/my/](https://moodle.scnu.edu.cn/my/) 且能看到你的课程列表

### 3. 导出 Cookie

使用下面任一方法导出 Cookie。

---

## 导出方法

### 方法一：使用浏览器扩展（推荐）

#### Chrome/Edge

1. 安装 [Cookie-Editor](https://microsoftedge.microsoft.com/addons/detail/cookieeditor/neaplmfkghagebokkhpjpoebhdledlfi)
2. 在砺儒云页面点击扩展图标
3. 选择 "Export" → "JSON"
4. Cookie 已复制到剪贴板

#### Firefox

1. 安装 [Cookie Quick Manager](https://addons.mozilla.org/zh-CN/firefox/addon/cookie-quick-manager/)
2. 在砺儒云页面点击扩展图标
3. 选择 Export → JSON
4. Cookie 已复制到剪贴板

---

### 方法二：使用开发者工具

1. 打开开发者工具：按 `F12`

2. 切换到 Console 标签

3. 粘贴并运行以下代码：

```javascript
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
console.log(JSON.stringify(cookies, null, 2));
```

4. 复制输出的 JSON 内容

---

## 常见问题

### Q: Cookie 安全吗？

A: **Cookie 等同于账号密码**，任何人拿到你的 Cookie 都可以以你的身份登录系统。请注意：
- 不要分享 Cookie 文件
- 不要上传到公开平台
- Cookie 有有效期：通常几小时到几天后会自动过期

### Q: 如何判断 Cookie 已过期？

A: 运行程序时如果提示"登录失败"，说明 Cookie 可能已过期，需要重新获取。

### Q: 为什么程序提示"登录失败"？

A: 常见原因：
1. **Cookie 已过期**：重新获取即可
2. **导出时机不对**：必须在登录成功并跳回砺儒云后导出，地址栏应显示 `moodle.scnu.edu.cn` 而不是 `https://sso.scnu.edu.cn/`

### Q: 如何验证导出的 Cookie 是否有效？

A: 检查 Cookie JSON 中必须包含：
```json
{
  "name": "MoodleSession",
  "value": "...",
  "domain": "moodle.scnu.edu.cn"
}
```
如果没有这个字段，可能是在登录页面或 SSO 页面导出的，需要等登录成功跳回砺儒云后再导出。
