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