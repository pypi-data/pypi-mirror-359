"""
美团 HTTP 请求模块

这个模块提供了带 SSO 登录态的 HTTP 请求功能。
"""

from .meituan_requests import MeituanRequests, RequestConfig

__all__ = [
    'MeituanRequests',  # 美团 HTTP 请求类
    'RequestConfig',    # 请求配置数据类
]
