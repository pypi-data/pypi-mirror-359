import json
import os
from typing import Dict, Optional
import webbrowser
from utils.logger import get_logger
from sso.config import STORAGE_PATH, AppConfig
from sso.browser_cookie_reader import BrowserCookieReader

logger = get_logger()

# SSO_COOKIE_KEYS = ['u2dhn6k', 'TGCN', 'TGCX','moa_token', 'webDeviceUuid']

SSO_COOKEY_KEY = 'TGCN'

class CookieManager:
    """Cookie管理器，负责读写cookie文件"""
    def __init__(self):
        # if self.is_only_read_cookie_from_browser():
        #         self.sso_cookies = self._load_sso_cookies_from_browser()
        #         if SSO_COOKEY_KEY not in self.sso_cookies:
        #             logger.error("SSO未登录，请打开浏览器登录后重试")
        #         webbrowser.open('https://ssosv.sankuai.com/sson/login')
        #         raise Exception("SSO未登录，请打开浏览器登录后重试")
        # else:
        #     local_sso_cookies = self._load_cookies_from_file(STORAGE_PATH['SSO_COOKIES'])
        #     if SSO_COOKEY_KEY in local_sso_cookies:
        #         # 如果本地有 TGCN，则使用本地 cookies
        #         self.sso_cookies = local_sso_cookies
        #         self._save_cookies(STORAGE_PATH['SSO_COOKIES'], self.sso_cookies)
        #     self.app_cookies = self._load_cookies_from_file(STORAGE_PATH['APP_COOKIES'])
        pass

    
    def  is_only_read_cookie_from_browser(self) -> bool:
        """是否只从浏览器读取cookie"""
        return os.getenv('ONLY_READ_COOKIE_FROM_BROWSER', '1') == '1'
        
    def _load_sso_cookies_from_browser(self) -> Dict:
        """从浏览器加载 SSO cookies"""
        try:
            logger.info("try get sso cookies from default browser")
            cookies = BrowserCookieReader.get_browser_cookies_from_default_browser(domain='ssosv.sankuai.com')
            if SSO_COOKEY_KEY in cookies:
                logger.info("got sso cookies from default browser")
                return cookies
            else:
                logger.warning("try get sso cookies from all browser")
                cookies = BrowserCookieReader.get_browser_cookies_from_all_browser(SSO_COOKEY_KEY, 'ssosv.sankuai.com')
                if SSO_COOKEY_KEY in cookies:
                    logger.info("got sso cookies from all browser")
                    return cookies
                else:
                    logger.error("SSO未登录，请打开浏览器登录后重试")
                    webbrowser.open('https://ssosv.sankuai.com/sson/login')
                    raise Exception("SSO未登录，请打开浏览器登录后重试")
        except Exception as e:
            logger.error(f"从浏览器读取 cookies 失败: {str(e)}")
            return self._load_cookies_from_file(STORAGE_PATH['SSO_COOKIES'])

    def _load_cookies_from_file(self, file_path: str) -> Dict[str, str]:
        try:
            with open(file_path, 'r') as f:
                content = json.load(f)
                return content
        except FileNotFoundError:
            return {}  # 文件不存在返回空字典
        except json.JSONDecodeError:
            return {}  # JSON解析错误返回空字典
        except Exception as e:
            logger.error(f"读取文件错误: {str(e)}")
            return {}

    def _save_cookies(self, file_path: str, cookies: Dict):
        try:
            with open(file_path, 'w') as f:
                json.dump(cookies, f, indent=2)
        except Exception as e:
            logger.error(f"保存cookies到文件失败: {str(e)}")
            raise

    def get_sso_cookies(self) -> Dict:
        # 每次获取 SSO cookies 时都重新从浏览器读取
        self.sso_cookies = self._load_sso_cookies_from_browser()
        return self.sso_cookies
    
    def get_sso_cookies_value(self, cookie_name: str) -> str:
        # 确保获取最新的 cookie 值
        return self.get_sso_cookies().get(cookie_name, '')

    def update_sso_cookies(self, cookies: Dict):
        self.sso_cookies.update(cookies)
        self._save_cookies(STORAGE_PATH['SSO_COOKIES'], self.get_sso_cookies())

    def get_app_cookies(self, client_id: str) -> Optional[Dict]:
        return self.app_cookies.get(client_id)

    def update_app_cookies_to_file(self, client_id: str, cookies: Dict):
        app_cookies = self.app_cookies.get(client_id, {})
        app_cookies.update(cookies)
        self.app_cookies[client_id] = app_cookies
        self._save_cookies(STORAGE_PATH['APP_COOKIES'], self.app_cookies)

    def clear_cookies(self):
        self.sso_cookies = {}
        self.app_cookies = {}
        self._save_cookies(STORAGE_PATH['SSO_COOKIES'], self.sso_cookies)
        self._save_cookies(STORAGE_PATH['APP_COOKIES'], self.app_cookies)
        
    def try_get_cookie_from_browser(self, app_config: AppConfig) -> Optional[Dict]:
        """尝试从浏览器获取cookie"""
        try:
            base_url = app_config.base_url
            if base_url.startswith('https://'):
                base_url = base_url[8:]
            elif base_url.startswith('http://'):
                base_url = base_url[7:]
            app_cookies =   BrowserCookieReader.get_browser_cookies_from_default_browser(domain=base_url)
            if app_cookies and app_config.ssoid_ck_name in app_cookies:
                return app_cookies
            else:
                logger.warning("try get app cookies from all browser")
                app_cookies = BrowserCookieReader.get_browser_cookies_from_all_browser(app_config.ssoid_ck_name, base_url)
                if app_cookies and app_config.ssoid_ck_name in app_cookies:
                    return app_cookies
                
            logger.error(f"app {app_config.client_id} 未登录，请打开浏览器登录后重试")
            webbrowser.open(app_config.base_url)
            return None
        except Exception as e:
            logger.error(f"{app_config.client_id} 从浏览器读取 cookies 失败: {str(e)}")
            return None