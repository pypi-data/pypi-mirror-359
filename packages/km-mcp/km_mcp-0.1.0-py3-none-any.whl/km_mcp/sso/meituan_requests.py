from dataclasses import dataclass
import webbrowser
import requests
from typing import Any, Dict, Optional
from sso.sso_manager import SSOManager
from sso.config import AppConfig, get_config_by_base_url
from utils.logger import get_logger

logger = get_logger()

meituan_sso_manager = SSOManager()

@dataclass
class RequestConfig:
    """请求配置数据类"""
    method: str = 'GET'
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    json: Optional[Dict[str, Any]] = None
    cookies: Optional[Dict[str, str]] = None
    timeout: Optional[int] = 30
    verify: bool = True
    allow_redirects: bool = False
    skip_sso: bool = False

class MeituanRequests:
    def __init__(self):
        self.sso_manager = meituan_sso_manager
        self.session = requests.Session()
    
    def _prepare_request(self, url: str, config: RequestConfig) -> requests.Request:
        """准备请求对象"""
        request = requests.Request(
            method=config.method,
            url=url,
            headers=config.headers or {},
            params=config.params,
            data=config.data,
            json=config.json,
            cookies=config.cookies or {}
        )
        return request

    def _handle_response(self, response: requests.Response, app_config: AppConfig, skip_sso: bool) -> requests.Response:
        """处理响应"""
        response.raise_for_status()
        if not skip_sso:
            if response.is_redirect or app_config.is_login_invalid(response):
                raise requests.RequestException("登录态过期")
        return response

    def request(self, url: str, config: RequestConfig = None) -> requests.Response:
        """发送HTTP请求"""
        if config is None:
            config = RequestConfig()

        try:
            app_config = None
            app_cookies = {}
            if not config.skip_sso:
                app_config = get_config_by_base_url(url)
                if not app_config:
                    raise requests.RequestException("无法获取应用配置")
                # 获取应用cookies
                app_cookies = self.sso_manager.get_app_cookies(app_config)
                if not app_cookies:
                    logger.error(f"无法获取应用cookies，client_id: {app_config.client_id}")
                    raise requests.RequestException("无法获取应用cookies")
                
           
            # 准备请求
            request = self._prepare_request(url, config)
             # 添加cookies
            request.cookies.update(app_cookies)
            prepared_request = self.session.prepare_request(request)
            response = self.session.send(
                prepared_request,
                timeout=config.timeout,
                verify=config.verify,
                allow_redirects=config.allow_redirects
            )
            # 处理响应
            return self._handle_response(response, app_config, config.skip_sso)
        
        except requests.RequestException as e:
            if str(e) == "登录态过期":
                # 登录态过期，尝试刷新
                logger.error(f"登录态过期，请登录后重试: {url}")
                webbrowser.open(app_config.base_url)
            raise
        except Exception as e:
            logger.error(f"HTTP请求失败: url: {url}  {e}")
            raise
    def get(self, url: str, **kwargs) -> requests.Response:
        """发送GET请求"""
        config = RequestConfig(method='GET', **kwargs)
        return self.request(url, config)

    def post(self, url: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """发送POST请求"""
        config = RequestConfig(method='POST', data=data, json=json, **kwargs)
        return self.request(url, config)

    def post_json(self, url: str, json_data: Dict[str, Any], **kwargs) -> requests.Response:
        """发送JSON格式的POST请求"""
        return self.post(url, json=json_data, **kwargs)

    def post_form(self, url: str, form_data: Dict[str, Any], **kwargs) -> requests.Response:
        """发送表单格式的POST请求"""
        return self.post(url, data=form_data, **kwargs)

    def ws_connect(self, url: str, headers: Optional[Dict[str, str]] = None, cookies: Optional[Dict[str, str]] = None, skip_sso: bool = False, **kwargs):
        """
        Establish a websocket connection with optional SSO cookies and custom headers.
        Args:
            url: websocket url (ws:// or wss://)
            headers: custom headers
            cookies: custom cookies, will be merged with SSO cookies if skip_sso is False
            skip_sso: whether to skip SSO cookie injection
            **kwargs: extra arguments for websocket.create_connection
        Returns:
            websocket.WebSocket: the websocket connection object
        """
        import websocket
        app_cookies = {}
        if not skip_sso:
            app_config = get_config_by_base_url(url)
            if not app_config:
                raise Exception("无法获取应用配置")
            app_cookies = self.sso_manager.get_app_cookies(app_config)
            if not app_cookies:
                logger.error(f"无法获取应用cookies，client_id: {app_config.client_id}")
                raise Exception("无法获取应用cookies")
        # 合并cookies
        merged_cookies = {}
        if app_cookies:
            merged_cookies.update(app_cookies)
        if cookies:
            merged_cookies.update(cookies)
        # 构造Cookie header
        cookie_header = None
        if merged_cookies:
            cookie_header = '; '.join(f"{k}={v}" for k, v in merged_cookies.items())
        ws_headers = headers.copy() if headers else {}
        try:
            ws = websocket.create_connection(url, header=[f"{k}: {v}" for k, v in ws_headers.items()], cookie=cookie_header, **kwargs)
            return ws
        except Exception as e:
            logger.error(f"WebSocket连接失败: url: {url}  {e}")
            raise

    def ws_connect_app(self, url: str, on_message=None, on_error=None, on_close=None, on_open=None, headers: Optional[Dict[str, str]] = None, cookies: Optional[Dict[str, str]] = None, skip_sso: bool = False, **kwargs):
        """
        基于WebSocketApp的事件驱动WebSocket连接，支持SSO cookie和自定义header。
        Args:
            url: websocket url (ws:// or wss://)
            on_message: 消息回调
            on_error: 错误回调
            on_close: 关闭回调
            on_open: 连接建立回调
            headers: 自定义header
            cookies: 自定义cookie，将与SSO cookie合并
            skip_sso: 是否跳过SSO cookie注入
            **kwargs: 传递给WebSocketApp的其他参数
        Returns:
            websocket.WebSocketApp: 事件驱动的WebSocket连接对象
        """
        import websocket
        app_cookies = {}
        if not skip_sso:
            app_config = get_config_by_base_url(url)
            if not app_config:
                raise Exception("无法获取应用配置")
            app_cookies = self.sso_manager.get_app_cookies(app_config)
            if not app_cookies:
                logger.error(f"无法获取应用cookies，client_id: {app_config.client_id}")
                raise Exception("无法获取应用cookies")
        # 合并cookies
        merged_cookies = {}
        if app_cookies:
            merged_cookies.update(app_cookies)
        if cookies:
            merged_cookies.update(cookies)
        # 构造Cookie header
        cookie_header = None
        if merged_cookies:
            cookie_header = '; '.join(f"{k}={v}" for k, v in merged_cookies.items())
        ws_headers = headers.copy() if headers else {}
        if cookie_header:
            ws_headers['Cookie'] = cookie_header
        ws = websocket.WebSocketApp(
            url,
            header=[f"{k}: {v}" for k, v in ws_headers.items()],
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open,
            **kwargs
        )
        return ws
