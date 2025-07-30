import requests
from typing import Dict, Optional
from sso.config import AppConfig
from sso.cookie_manager import CookieManager
from utils.logger import get_logger
import webbrowser

# 配置logger
logger = get_logger()

class SSOManager:
    def __init__(self):
        self.cookie_manager = CookieManager()
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self) -> None:
        """设置session的基本配置"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        })

    def get_app_cookies(self, app_config: AppConfig) -> Optional[Dict[str, str]]:
        """获取应用的cookie"""
        return self.cookie_manager.try_get_cookie_from_browser(app_config)
       
        # else:
        #     app_cookies = self.cookie_manager.get_app_cookies(app_config.client_id)
        #     if not app_cookies and self.login_app_with_sso(app_config):
        #         app_cookies = self.cookie_manager.get_app_cookies(app_config.client_id)
        # return app_cookies


    # def _get_u2dhn6k(self) -> str:
    #     """获取u2dhn6k"""
    #     u2dhn6k = self.cookie_manager.get_sso_cookies_value('u2dhn6k')
    #     if u2dhn6k:
    #         return u2dhn6k
    #     u2dhn6k = os.getenv('U2DHN6K')
    #     if u2dhn6k:
    #         return u2dhn6k
    #     u2dhn6k = uuid.uuid4().hex
    #     self.session.post(SSO_CONFIG['SSO_QRCODE_URL'] + '/sson/web/device/info/report', data={'random_id': u2dhn6k}, params={'u2dhn6k': u2dhn6k})
    #     self.cookie_manager.update_sso_cookies({'u2dhn6k': u2dhn6k})
    #     return u2dhn6k

    # def _get_moa_info(self, lt: str, client_id: str) -> Dict:
    #     """获取MOA信息"""
    #     u2dhn6k = self._get_u2dhn6k()
        
    #     # 获取moaRandom
    #     moa_url = f"{SSO_CONFIG['SSO_MOA_URL']}/random"
    #     params = {
    #         'u2dhn6k': u2dhn6k,
    #         'lt': lt
    #     }
    #     response = self.session.get(moa_url, params=params)
    #     moa_random = response.json()['data']
        
    #     # 通过WebSocket获取moaInfo
    #     try:
    #         ws = websocket.create_connection(SSO_CONFIG['MOA_WS_URL'])
        
    #         message = {
    #             'command': 'queryStatus',
    #             'random': moa_random,
    #             'msgType': '102',
    #             'ssoVersion': '',
    #             't': int(time.time() * 1000)
    #         }
    #         ws.send(json.dumps(message))
    #         response = ws.recv()
    #         ws.close()
    #         return json.loads(response)
    #     except Exception as e:
    #         logger.error(f"moa状态异常，需安装moa: {e}")
    #         raise
        
    # def _get_qr_code(self, client_id: str) -> str:
    #     """获取登录二维码"""
    #     timestamp = int(time.time() * 1000)
    #     u2dhn6k = self._get_u2dhn6k()
        
    #     # 获取UUID
    #     uuid_url = f"{SSO_CONFIG['SSO_QRCODE_URL']}/getuuid"
    #     params = {
    #         'time': timestamp,
    #         'u2dhn6k': u2dhn6k
    #     }
    #     response = self.session.get(uuid_url, params=params)
    #     uuid = response.json()['uuid']
        
    #     # 生成二维码
    #     qr_url = f"{SSO_CONFIG['SSO_QRCODE_URL']}/{uuid}?locale=zh"
    #     qr = qrcode.QRCode()
    #     qr.add_data(qr_url)
    #     qr.make()
    #     img = qr.make_image()
    #     img.save('login_qr.png')
    #     logger.info("请使用大象扫描二维码 login_qr.png")
    #     return uuid

    # def login(self, app_config: AppConfig) -> bool:
    #     """扫描二维码执行SSO登录流程"""
    #     # 访问登录页获取初始cookie
    #     login_url = SSO_CONFIG['SSO_LOGIN_URL'] 
    #     params = {
    #         'client_id':  app_config.client_id if app_config.client_id != "mws_test" else "60921859",
    #         'redirect_uri': f"{app_config.redirect_uri}?original-url=%2F&locale=zh"
    #     }
    #     response = self.session.get(login_url, params=params)
        
    #     # 使用正则表达式安全地获取lt值
    #     lt_match = re.search(r'name="lt" value="([^"]+)"', response.text)
    #     if not lt_match:
    #         logger.error("无法获取lt值，登录失败")
    #         return False
    #     lt = lt_match.group(1)

    #     # 获取登录二维码
    #     uuid = self._get_qr_code(app_config.client_id)
    #     data = {
    #         'uuid': uuid,
    #         'service': '',
    #         'appkey': app_config.client_id,
    #         'lt': lt
    #     }
    #     # 获取MOA信息
    #     moa_info = self._get_moa_info(data['lt'], app_config.client_id)
    #     moa_json = {
    #         'type': 'success',
    #         'data': moa_info
    #     }
    #     status_url = f"{SSO_CONFIG['SSO_QRCODE_URL']}/login"
    #     while True:
    #         time.sleep(2)
    #         response = self.session.post(status_url, data=data)
    #         result = response.json()
    #         if result['code'] == 201:
    #             # 完成登录
    #             success_url = f"{SSO_CONFIG['SSO_QRCODE_URL']}/login/success"
    #             params = {
    #                 'lt': data['lt'],
    #                 'uuid': uuid,
    #                 't': int(time.time() * 1000),
    #                 'moaInfo': json.dumps(moa_json),
    #                 'locale': 'zh',
    #                 'ssoGrayTag': app_config.client_id
    #             }
    #             response = self.session.get(success_url, params=params, allow_redirects=False)
    #             # 登录成功后有2次重定向，
    #             #   - 第一次303重定向到地址：/sson/oauth2.0/callbackAuthorize?code=xxx&lt=xxx 
    #             #   - 第二次重定向到应用callback地址
    #             if response.status_code != 200:
    #                 logger.error(f"登录异常: {response.text}")
    #                 return False
    #             if response.status_code == 303 and response.headers.get('Location'):
    #                 redirect_url = response.headers.get('Location')
    #                 if redirect_url and redirect_url.startswith('/sson/oauth2.0/callbackAuthorize'):
    #                     # 保存SSO cookie
    #                     self.cookie_manager.update_sso_cookies(response.cookies.get_dict())
    #                     # 访问callback地址获取app的cookie
    #                     auth_response = self.session.get(f"{SSO_CONFIG['SSO_BASE_URL']}{redirect_url}")
    #                     if auth_response.status_code == 303 and auth_response.headers.get('Location'):
    #                         redirect_url = auth_response.headers.get('Location')
    #                         # 访问callback地址获取app的cookie
    #                         return self.refresh_app_cookie_by_callback(app_config, redirect_url)
    #             return True
    #         elif result['code'] == 500:
    #             continue
    #         else:
    #             return False

    # def login_app_with_browser(self, app_config: AppConfig) -> bool:
    #     app_cookies = self.cookie_manager.try_get_cookie_from_browser(app_config)
    #     if app_cookies:
    #         self.cookie_manager.update_app_cookies_to_file(app_config.client_id, app_cookies)
    #         return True
    #     else:
    #         logger.error(f"app {app_config.client_id} 未登录，请打开浏览器登录后重试")
    #         webbrowser.open(app_config.base_url)
    #         return False
    
    # def login_app_with_sso(self, app_config: AppConfig) -> bool:
       
    #     """SSO已经登录，使用SSO cookie访问应用"""
    #     sso_cookies = self.cookie_manager.get_sso_cookies()
    #     if not sso_cookies:
    #         logger.info(" https://ssosv.sankuai.com/sson/login 进行登录")
    #         webbrowser.open('https://ssosv.sankuai.com/sson/login')
    #         return False
    #     self.cookie_manager.update_sso_cookies(sso_cookies)
    #     self.session.cookies.update(sso_cookies)
    #     params = {
    #         'client_id':  app_config.client_id if app_config.client_id != "mws_test" else "60921859",
    #         'redirect_uri': f"{app_config.redirect_uri}?original-url=%2F&locale=zh"
    #     }
    #     # 使用SSO Cookie更新app cookie
    #     response = self.session.get(SSO_CONFIG['SSO_LOGIN_URL'], params=params, allow_redirects=False)
    #     return  self._refresh_cookies_by_login(response, app_config)    
    
    # def _refresh_cookies_by_login(self, response: requests.Response, app_config:AppConfig) -> bool:
    #     logger.info(f"刷新cookies {response.status_code} {response.headers.get('Location')}, app_config: {app_config.client_id},response.cookies: {len(response.cookies.get_dict())}, response.text: {response.text if response.text else 'empty'}")
    #     if response.status_code == 303 and response.headers.get('Location'):
    #         redirect_url = response.headers.get('Location')
    #         if redirect_url:
    #             # 保存SSO cookie
    #             self.cookie_manager.update_sso_cookies(self.session.cookies.get_dict())
    #             # 访问callback地址获取app的cookie
    #             return self.refresh_app_cookie_by_callback(app_config, redirect_url)
    #     return False
    
    # def refresh_app_cookie_by_callback(self, app_config, redirect_url) -> bool :
    #     logger.info(f"刷新app cookie1 {redirect_url}, app_config: {app_config.client_id}")
    #     app_callback_response = self.session.get(redirect_url, allow_redirects=False)
    #     app_cookies = self.session.cookies.get_dict()
    #     if not app_cookies and  not app_callback_response.text:
    #         logger.info(f"refresh sso failed, try to get cookie from browser redirect_url: {redirect_url}  client_id: {app_config.client_id}")
    #     if app_callback_response.text:
    #         app_cookies[app_config.ssoid_ck_name] = app_callback_response.text
    #     if app_cookies and app_config.ssoid_ck_name in app_cookies:
    #         self.cookie_manager.update_app_cookies_to_file(app_config.client_id, app_cookies)
    #         return True
        
    #     logger.info(f"refresh sso failed, try to get cookie from browser {app_config.client_id}")
    #     app_cookies  = self.cookie_manager.try_get_cookie_from_browser(app_config)
    #     if app_cookies and app_config.ssoid_ck_name in app_cookies:
    #         self.cookie_manager.update_app_cookies_to_file(app_config.client_id, app_cookies)
    #         return True
    #     return False
    
    # def logout(self):
    #     self.cookie_manager.clear_cookies()
    #     self.session.get(SSO_CONFIG['SSO_LOGOUT_URL'])
        