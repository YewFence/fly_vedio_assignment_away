# convert_cookies.py
import json

# 读取浏览器导出的Cookie
with open('browser_cookies.json', 'r') as f:
    browser_cookies = json.load(f)

# 转换为Playwright格式
playwright_cookies = []
for cookie in browser_cookies:
    # 处理 sameSite: null/空字符串 -> 'Lax'，其他值标准化首字母大写
    same_site = cookie.get('sameSite')
    if same_site is None or same_site == '':
        same_site = 'Lax'
    elif isinstance(same_site, str):
        # 标准化为首字母大写格式
        same_site_lower = same_site.lower()
        if same_site_lower in ['lax', 'strict', 'none']:
            same_site = same_site_lower.capitalize()
        elif same_site_lower in ['unspecified', 'no_restriction']:
            same_site = 'Lax'
        else:
            same_site = 'Lax'

    playwright_cookie = {
        'name': cookie.get('name'),
        'value': cookie.get('value'),
        'domain': cookie.get('domain'),
        'path': cookie.get('path') or '/',
        'expires': cookie.get('expirationDate', -1),
        'httpOnly': cookie.get('httpOnly', False),
        'secure': cookie.get('secure', False),
        'sameSite': same_site
    }
    playwright_cookies.append(playwright_cookie)

# 保存
with open('cookies.json', 'w', encoding='utf-8') as f:
    json.dump(playwright_cookies, f, indent=2, ensure_ascii=False)

print("✓ Cookie转换完成!")