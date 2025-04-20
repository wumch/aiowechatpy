# -*- coding: utf-8 -*-
import unittest

from aiowechatpy import WeChatClient
from aiowechatpy.client.api import WeChatMessage


class SendMessageTestCase(unittest.TestCase):
    def setUp(self):
        self.client = WeChatClient("wx1234567887654321", "secret")
        self.message = WeChatMessage(self.client)

    def test_get_subscribe_authorize_url(self):
        scene = 42
        template_id = "some_long_id"
        redirect_url = "https://mp.weixin.qq.com"
        reserved = "random_string"
        url = self.message.get_subscribe_authorize_url(scene, template_id, redirect_url, reserved)
        expected_url = (
            f"https://mp.weixin.qq.com/mp/subscribemsg?action=get_confirm&"
            f"appid={self.client.appid}&scene={scene}&template_id={template_id}&"
            f"redirect_url=https%3A%2F%2Fmp.weixin.qq.com&reserved={reserved}#wechat_redirect"
        )
        self.assertEqual(expected_url, url)

    def test_send_template_message_miniprogram(self):
        res = self.message.send_subscribe_message_miniprogram(
            openid="oKeJX7PI-Y59hfwxHFY_l6Jsjqfs",
            template_id="nFoAUjYoDZWdiiAjb8p272OxR4tT1Egse1zwGaKbSNc",
            data={
                "thing1": {"value": "徐记海鲜"},
                "amount2": {"value": "3.66"},
                "thing3": {"value": "需点击领取红包"},
            },
            page='pages/apply/apply?bill=12049&credence=5f9cd9',
        )
