# convert_cookies.py
import json
import sys

def cookie_fix():
    try:
        # 从CLI读取浏览器导出的Cookie
        print("请粘贴浏览器导出的Cookie JSON (连续敲击两次回车(Enter)结束输入):")
        lines = list(iter(input, ''))
        content = '\n'.join(lines)
        
        if content == '':
            print("✗ 输入为空，请检查输入内容")
            return False
        browser_cookies = json.loads(content)

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
        return True
    except Exception as e:
        print(f"✗ Cookie转换失败: {e}")
        return False