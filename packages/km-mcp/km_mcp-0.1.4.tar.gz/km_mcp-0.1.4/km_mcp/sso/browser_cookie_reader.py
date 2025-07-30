import browser_cookie3
import os
from typing import Dict
import webbrowser

from ..utils.logger import get_logger

logger = get_logger()

class BrowserCookieReader:
    SUPPORTED_BROWSERS = {
        'chrome': browser_cookie3.chrome,
        'firefox': browser_cookie3.firefox,
        'edge': browser_cookie3.edge,
        'opera': browser_cookie3.opera,
        'brave': browser_cookie3.brave,
        'chromium': browser_cookie3.chromium,
        'lynx': browser_cookie3.lynx,
        'arc': browser_cookie3.arc
    }

    @classmethod
    def get_browser_type(cls) -> str:
        """从环境变量获取浏览器类型，默认为 chrome"""
        browser_type = os.environ.get('my_default_browser', 'chrome').lower()
        if browser_type not in cls.SUPPORTED_BROWSERS:
            raise ValueError(f"Unsupported browser type: {browser_type}. Supported types: {list(cls.SUPPORTED_BROWSERS.keys())}")
        return browser_type
    
    @classmethod
    def get_browser_cookies_from_default_browser(cls, domain: str) -> Dict[str, str]:
        """从默认浏览器读取cookies"""
        browser_type = cls.get_browser_type()
        reader = cls.SUPPORTED_BROWSERS[browser_type]
        specified_cookie_file_path = os.environ.get('MY_COOKIE_FILE', None)
        if specified_cookie_file_path:
            specified_cookie_file_path = os.path.expanduser(specified_cookie_file_path)
            browser_cookies = reader(domain_name=domain, cookie_file=specified_cookie_file_path)
        else:
            browser_cookies = reader(domain_name=domain)
        return {cookie.name: cookie.value for cookie in browser_cookies}
    
    @classmethod
    def get_browser_cookies_from_all_browser(cls, cookie_key: str, domain: str) -> Dict[str, str]:
        """从所有浏览器读取cookies"""
        for browser, reader in cls.SUPPORTED_BROWSERS.items():
            try:
                browser_cookies = reader(domain_name=domain)
                cookies = {cookie.name: cookie.value for cookie in browser_cookies}
                if cookie_key in cookies:
                    return cookies
            except Exception as e:
                logger.warning(f"从 {browser} 读取cookies失败: {str(e)}")
                continue


# 使用示例
if __name__ == "__main__":
        cookie_keys = ['u2dhn6k', 'TGCN', 'TGCX', 'moa_token', 'webDeviceUuid']
        domain = 'ssosv.sankuai.com'
        """从所有支持的浏览器中获取 cookies，直到找到 TGCN 为止"""
        # 从所有支持的浏览器中获取 cookies，直到找到 TGCN 为止
        for browser in BrowserCookieReader.SUPPORTED_BROWSERS.keys():
            try:
                cookies = BrowserCookieReader.read_cookies(cookie_keys, domain)
                if 'TGCN' in cookies:
                    logger.info(f"从 {browser} 获取到的 cookies: {cookies}")
                    break
            except Exception as e:
                logger.warning(f"从 {browser} 获取 cookies 失败: {str(e)}")
