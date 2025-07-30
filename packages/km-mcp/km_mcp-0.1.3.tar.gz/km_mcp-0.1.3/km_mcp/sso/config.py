from dataclasses import dataclass, field
from typing import Callable
import os

import requests


SSO_CONFIG = {
    'SSO_BASE_URL': 'https://ssosv.sankuai.com',
    'SSO_LOGIN_URL': 'https://ssosv.sankuai.com/sson/login',
    'SSO_QRCODE_URL': 'https://ssosv.sankuai.com/sson/qrcode',
    'SSO_MOA_URL': 'https://ssosv.sankuai.com/sson/moa',
    'MOA_WS_URL': 'wss://localhost.moa.sankuai.com:16161',
    'COOKIE_EXPIRE_DAYS': 14,
    'REFRESH_THRESHOLD_DAYS': 5,
}

# 存储路径配置
STORAGE_PATH = {
    'SSO_COOKIES': os.path.abspath(os.path.join(os.path.dirname(__file__), 'sso_cookies.json')),
    'APP_COOKIES': os.path.abspath(os.path.join(os.path.dirname(__file__), 'app_cookies.json'))
} 

@dataclass
class AppConfig:
    client_id: str
    sso_callback_uri: str
    base_url: str
    is_login_invalid: Callable[[requests.Response], bool] = field(default=lambda response: response.status_code == 401 or response.is_redirect)
    ssoid_key:str = field(default='')
    @property
    def redirect_uri(self) -> str:
        return f"{self.base_url}{self.sso_callback_uri}"
    
    @property
    def ssoid_ck_name(self) -> str:
        if self.ssoid_key:
            return self.ssoid_key
        else:
            return f"{self.client_id}_ssoid"

KM_CONFIG = AppConfig(
    client_id='com.sankuai.it.ead.citadel', 
    sso_callback_uri='/sso/callback', 
    base_url='https://km.sankuai.com', 
    is_login_invalid=lambda response: response.status_code == 401
)

WanXiang_CONFIG = AppConfig(
    client_id='com.sankuai.data.wanxiang.wanxiang', 
    sso_callback_uri='/wxapi/sso/callback', 
    base_url='https://data.sankuai.com', 
    is_login_invalid=lambda response: response.status_code == 401
)

MWS_CONFIG = AppConfig(
    ssoid_key='yun_portal_ssoid',
    client_id='60921859', 
    sso_callback_uri='/sso/callback', 
    base_url='https://mws.sankuai.com', 
    is_login_invalid=lambda response: response.status_code == 401
)

MWS_TEST_CONFIG = AppConfig(
    ssoid_key=MWS_CONFIG.ssoid_key,
    client_id="mws_test",
    sso_callback_uri=MWS_CONFIG.sso_callback_uri, 
    base_url='https://mws-test.sankuai.com', 
    is_login_invalid=MWS_CONFIG.is_login_invalid
)
DEVTOOLS_CONFIG = AppConfig(
    ssoid_key="f32a546874_ssoid",
    client_id="f32a546874",
    sso_callback_uri="/sso/callback", 
    base_url='https://dev.sankuai.com', 
    is_login_invalid=lambda response: response.status_code == 401
)

def get_config_by_base_url(url: str) -> AppConfig:
    if url.startswith(KM_CONFIG.base_url):
        return KM_CONFIG
    elif url.startswith(DEVTOOLS_CONFIG.base_url):
        return DEVTOOLS_CONFIG
    elif url.startswith(WanXiang_CONFIG.base_url):
        return WanXiang_CONFIG
    elif '.mws-test.sankuai.com' in url or 'logcenterv2.inf.test.sankuai.com/' in url:
        return MWS_TEST_CONFIG
    elif '.mws.sankuai.com' in url or 'raptor-logcenterv2.sankuai.com' in url:
        return MWS_CONFIG
    else:
        raise ValueError(f'不支持的base_url: {url}')