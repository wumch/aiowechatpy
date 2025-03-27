# -*- coding: utf-8 -*-


from aiowechatpy.client.base import BaseWeChatClient
from aiowechatpy.iot.client import api


class IotClient(BaseWeChatClient):
    """
    微信硬件接口
    https://iot.weixin.qq.com/doc
    """

    API_BASE_URL = "https://api.weixin.qq.com/ilink/api/"

    cloud = api.IotCloud()
    device = api.IotDevice()

    def __init__(
        self,
        app_id,
        secret,
        session=None,
        timeout=None,
        auto_retry=True,
    ):
        self.app_id = app_id
        self.secret = secret
        super().__init__(app_id, session, timeout, auto_retry)

    @property
    def access_token_key(self):
        return f"{self.app_id}_{self.secret[:10]}_access_token"

    async def fetch_access_token(self):
        """Fetch access token"""
        return await self._fetch_access_token(
            url="https://api.weixin.qq.com/cgi-bin/token",
            params={"grant_type": "client_credential", "appid": self.app_id, "secret": self.secret},
        )
