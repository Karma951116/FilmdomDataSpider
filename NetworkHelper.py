import requests
from fake_user_agent import user_agent


class NetworkHelper:
    """
    单例模式的网络助手，用于发送和接收请求
    """
    _is_proxy = False
    _proxy = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(NetworkHelper, cls).__new__(cls)
        return cls._instance

    def set_proxy(self, proxy):
        self._is_proxy = proxy

    def get(self, url: str, proxy=False, header=None):
        # ua = user_agent()
        # TODO: proxy on/off

        headers = {
            'Connection': 'keep-alive',
        }

        if header is not None:
            headers.update(header)

        return requests.get(url=url, headers=headers, timeout=10)
