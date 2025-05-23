# -*- coding: utf-8 -*-
import io
import json
import os
import inspect
import time
import unittest
from datetime import datetime

from httmock import HTTMock, response, urlmatch

from aiowechatpy import WeChatClient
from aiowechatpy.exceptions import WeChatClientException
from aiowechatpy.schemes import JsApiCardExt

_TESTS_PATH = os.path.abspath(os.path.dirname(__file__))
_FIXTURE_PATH = os.path.join(_TESTS_PATH, "fixtures")


@urlmatch(netloc=r"(.*\.)?api\.weixin\.qq\.com$")
def wechat_api_mock(url, request):
    path = url.path.replace("/cgi-bin/", "").replace("/", "_")
    if path.startswith("_"):
        path = path[1:]
    res_file = os.path.join(_FIXTURE_PATH, f"{path}.json")
    content = {
        "errcode": 99999,
        "errmsg": f"can not find fixture {res_file}",
    }
    headers = {"Content-Type": "application/json"}
    try:
        with open(res_file, "rb") as f:
            content = json.loads(f.read().decode("utf-8"))
    except (IOError, ValueError) as e:
        content["errmsg"] = f"Loads fixture {res_file} failed, error: {e}"
    return response(200, content, headers, request=request)


class WeChatClientTestCase(unittest.TestCase):
    app_id = "123456"
    secret = "123456"

    def setUp(self):
        self.client = WeChatClient(self.app_id, self.secret)

    def test_two_client_not_equal(self):
        client2 = WeChatClient("654321", "654321", "987654321")
        self.assertNotEqual(self.client, client2)
        self.assertNotEqual(self.client.user, client2.user)
        self.assertNotEqual(id(self.client.menu), id(client2.menu))
        with HTTMock(wechat_api_mock):
            self.client.fetch_access_token()
            self.assertNotEqual(self.client.access_token, client2.access_token)

    def test_subclass_client_ok(self):
        class TestClient(WeChatClient):
            pass

        client = TestClient("12345", "123456", "123456789")
        self.assertEqual(client, client.user._client)

    def test_fetch_access_token_is_method(self):
        self.assertTrue(inspect.ismethod(self.client.fetch_access_token))

        class TestClient(WeChatClient):
            @property
            def fetch_access_token(self):
                pass

        client = TestClient("12345", "123456", "123456789")
        self.assertFalse(inspect.ismethod(client.fetch_access_token))

    def test_fetch_access_token(self):
        with HTTMock(wechat_api_mock):
            token = self.client.fetch_access_token()
            self.assertEqual("1234567890", token["access_token"])
            self.assertEqual(7200, token["expires_in"])
            self.assertEqual("1234567890", self.client.access_token)

    def test_upload_media(self):
        media_file = io.StringIO("nothing")
        with HTTMock(wechat_api_mock):
            media = self.client.media.upload("image", media_file)
            self.assertEqual("image", media["type"])
            self.assertEqual("12345678", media["media_id"])

    def test_user_get_group_id(self):
        with HTTMock(wechat_api_mock):
            group_id = self.client.user.get_group_id("123456")
            self.assertEqual(102, group_id)

    def test_create_group(self):
        with HTTMock(wechat_api_mock):
            group = self.client.group.create("test")
            self.assertEqual(1, group["group"]["id"])
            self.assertEqual("test", group["group"]["name"])

    def test_group_get(self):
        with HTTMock(wechat_api_mock):
            groups = self.client.group.get()
            self.assertEqual(5, len(groups))

    def test_group_getid(self):
        with HTTMock(wechat_api_mock):
            group = self.client.group.get("123456")
            self.assertEqual(102, group)

    def test_group_update(self):
        with HTTMock(wechat_api_mock):
            result = self.client.group.update(102, "test")
            self.assertEqual(0, result["errcode"])

    def test_group_move_user(self):
        with HTTMock(wechat_api_mock):
            result = self.client.group.move_user("test", 102)
            self.assertEqual(0, result["errcode"])

    def test_group_delete(self):
        with HTTMock(wechat_api_mock):
            result = self.client.group.delete(123456)
            self.assertEqual(0, result["errcode"])

    def test_send_text_message(self):
        with HTTMock(wechat_api_mock):
            result = self.client.message.send_text(1, "test", account="test")
            self.assertEqual(0, result["errcode"])

    def test_send_image_message(self):
        with HTTMock(wechat_api_mock):
            result = self.client.message.send_image(1, "123456")
            self.assertEqual(0, result["errcode"])

    def test_send_voice_message(self):
        with HTTMock(wechat_api_mock):
            result = self.client.message.send_voice(1, "123456")
            self.assertEqual(0, result["errcode"])

    def test_send_video_message(self):
        with HTTMock(wechat_api_mock):
            result = self.client.message.send_video(1, "123456", "test", "test")
            self.assertEqual(0, result["errcode"])

    def test_send_music_message(self):
        with HTTMock(wechat_api_mock):
            result = self.client.message.send_music(
                1, "http://www.qq.com", "http://www.qq.com", "123456", "test", "test"
            )
            self.assertEqual(0, result["errcode"])

    def test_send_articles_message(self):
        with HTTMock(wechat_api_mock):
            articles = [
                {"title": "test", "description": "test", "url": "http://www.qq.com", "image": "http://www.qq.com"}
            ]
            result = self.client.message.send_articles(1, articles)
            self.assertEqual(0, result["errcode"])

    def test_send_card_message(self):
        with HTTMock(wechat_api_mock):
            result = self.client.message.send_card(1, "123456")
            self.assertEqual(0, result["errcode"])

    def test_send_mini_program_page(self):
        with HTTMock(wechat_api_mock):
            result = self.client.message.send_mini_program_page(1, {})
            self.assertEqual(0, result["errcode"])

    def test_send_mass_text_message(self):
        with HTTMock(wechat_api_mock):
            result = self.client.message.send_mass_text("test", [1])
            self.assertEqual(0, result["errcode"])

    def test_send_mass_image_message(self):
        with HTTMock(wechat_api_mock):
            result = self.client.message.send_mass_image("123456", [1])
            self.assertEqual(0, result["errcode"])

    def test_send_mass_voice_message(self):
        with HTTMock(wechat_api_mock):
            result = self.client.message.send_mass_voice("test", [1])
            self.assertEqual(0, result["errcode"])

    def test_send_mass_video_message(self):
        with HTTMock(wechat_api_mock):
            result = self.client.message.send_mass_video("test", [1], title="title", description="desc")
            self.assertEqual(0, result["errcode"])

    def test_send_mass_article_message(self):
        with HTTMock(wechat_api_mock):
            result = self.client.message.send_mass_article("test", [1])
            self.assertEqual(0, result["errcode"])

    def test_send_mass_card_message(self):
        with HTTMock(wechat_api_mock):
            result = self.client.message.send_mass_card("test", [1])
            self.assertEqual(0, result["errcode"])

    def test_get_mass_message(self):
        with HTTMock(wechat_api_mock):
            result = self.client.message.get_mass(201053012)
            self.assertEqual("SEND_SUCCESS", result["msg_status"])

    def test_create_menu(self):
        with HTTMock(wechat_api_mock):
            result = self.client.menu.create({"button": [{"type": "click", "name": "test", "key": "test"}]})
            self.assertEqual(0, result["errcode"])

    def test_get_menu(self):
        with HTTMock(wechat_api_mock):
            menu = self.client.menu.get()
            self.assertTrue("menu" in menu)

    def test_delete_menu(self):
        with HTTMock(wechat_api_mock):
            result = self.client.menu.delete()
            self.assertEqual(0, result["errcode"])

    def test_update_menu(self):
        with HTTMock(wechat_api_mock):
            result = self.client.menu.update({"button": [{"type": "click", "name": "test", "key": "test"}]})
            self.assertEqual(0, result["errcode"])

    def test_short_url(self):
        with HTTMock(wechat_api_mock):
            result = self.client.misc.short_url("http://www.qq.com")
            self.assertEqual("http://qq.com", result["short_url"])

    def test_get_wechat_ips(self):
        with HTTMock(wechat_api_mock):
            result = self.client.misc.get_wechat_ips()
            self.assertEqual(["127.0.0.1"], result)

    def test_check_network(self):
        with HTTMock(wechat_api_mock):
            result = self.client.misc.check_network()
            dns = result["dns"]
            self.assertListEqual(
                dns,
                [
                    {"ip": "111.161.64.40", "real_operator": "UNICOM"},
                    {"ip": "111.161.64.48", "real_operator": "UNICOM"},
                ],
            )

    def test_get_user_info(self):
        with HTTMock(wechat_api_mock):
            openid = "o6_bmjrPTlm6_2sgVt7hMZOPfL2M"
            user = self.client.user.get(openid)
            self.assertEqual("Band", user["nickname"])

    def test_get_followers(self):
        with HTTMock(wechat_api_mock):
            result = self.client.user.get_followers()
            self.assertEqual(2, result["total"])
            self.assertEqual(2, result["count"])

    def test_iter_followers(self):
        @urlmatch(netloc=r"(.*\.)?api\.weixin\.qq\.com$", query=r".*next_openid=[^&]+")
        def next_openid_mock(url, request):
            """伪造第二页的请求"""
            content = {"total": 2, "count": 0, "next_openid": ""}
            headers = {"Content-Type": "application/json"}
            return response(200, content, headers, request=request)

        with HTTMock(next_openid_mock, wechat_api_mock):
            users = list(self.client.user.iter_followers())
            self.assertEqual(2, len(users))
            self.assertIn("OPENID1", users)
            self.assertIn("OPENID2", users)

    def test_update_user_remark(self):
        with HTTMock(wechat_api_mock):
            openid = "openid"
            remark = "test"
            result = self.client.user.update_remark(openid, remark)
            self.assertEqual(0, result["errcode"])

    def test_get_user_info_batch(self):
        user_list = [
            {"openid": "otvxTs4dckWG7imySrJd6jSi0CWE", "lang": "zh-CN"},
            {"openid": "otvxTs_JZ6SEiP0imdhpi50fuSZg", "lang": "zh-CN"},
        ]
        with HTTMock(wechat_api_mock):
            result = self.client.user.get_batch(user_list)
            self.assertEqual(user_list[0]["openid"], result[0]["openid"])
            self.assertEqual("iWithery", result[0]["nickname"])
            self.assertEqual(user_list[1]["openid"], result[1]["openid"])

    def test_get_user_info_batch_openid_list(self):
        user_list = ["otvxTs4dckWG7imySrJd6jSi0CWE", "otvxTs_JZ6SEiP0imdhpi50fuSZg"]
        with HTTMock(wechat_api_mock):
            result = self.client.user.get_batch(user_list)
            self.assertEqual(user_list[0], result[0]["openid"])
            self.assertEqual("iWithery", result[0]["nickname"])
            self.assertEqual(user_list[1], result[1]["openid"])

    def test_get_tag_users(self):
        with HTTMock(wechat_api_mock):
            result = self.client.tag.get_tag_users(101)
            self.assertEqual(2, result["count"])

    def test_iter_tag_users(self):
        @urlmatch(netloc=r"(.*\.)?api\.weixin\.qq\.com$", path=r".*user/tag/get")
        def next_openid_mock(url, request):
            """伪造第二页的请求"""
            data = json.loads(request.body.decode())
            if not data.get("next_openid"):
                return wechat_api_mock(url, request)

            # 根据拿到的第二页请求响应 是没有data和next_openid的
            content = {"count": 0}
            headers = {"Content-Type": "application/json"}
            return response(200, content, headers, request=request)

        with HTTMock(next_openid_mock, wechat_api_mock):
            users = list(self.client.tag.iter_tag_users(101))
            self.assertEqual(2, len(users))
            self.assertIn("OPENID1", users)
            self.assertIn("OPENID2", users)

    def test_create_qrcode(self):
        data = {
            "expire_seconds": 1800,
            "action_name": "QR_SCENE",
            "action_info": {"scene": {"scene_id": 123}},
        }
        with HTTMock(wechat_api_mock):
            result = self.client.qrcode.create(data)
            self.assertEqual(1800, result["expire_seconds"])

    def test_get_qrcode_url_with_str_ticket(self):
        ticket = "123"
        url = self.client.qrcode.get_url(ticket)
        self.assertEqual("https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=123", url)

    def test_get_qrcode_url_with_dict_ticket(self):
        ticket = {
            "ticket": "123",
        }
        url = self.client.qrcode.get_url(ticket)
        self.assertEqual("https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=123", url)

    def test_customservice_add_account(self):
        with HTTMock(wechat_api_mock):
            result = self.client.customservice.add_account("test1@test", "test1", "test1")
            self.assertEqual(0, result["errcode"])

    def test_customservice_update_account(self):
        with HTTMock(wechat_api_mock):
            result = self.client.customservice.update_account("test1@test", "test1", "test1")
            self.assertEqual(0, result["errcode"])

    def test_customservice_delete_account(self):
        with HTTMock(wechat_api_mock):
            result = self.client.customservice.delete_account(
                "test1@test",
            )
            self.assertEqual(0, result["errcode"])

    def test_customservice_upload_headimg(self):
        media_file = io.StringIO("nothing")
        with HTTMock(wechat_api_mock):
            result = self.client.customservice.upload_headimg("test1@test", media_file)
            self.assertEqual(0, result["errcode"])

    def test_customservice_get_accounts(self):
        with HTTMock(wechat_api_mock):
            result = self.client.customservice.get_accounts()
            self.assertEqual(2, len(result))

    def test_customservice_get_online_accounts(self):
        with HTTMock(wechat_api_mock):
            result = self.client.customservice.get_online_accounts()
            self.assertEqual(2, len(result))

    def test_customservice_create_session(self):
        with HTTMock(wechat_api_mock):
            result = self.client.customservice.create_session("openid", "test1@test")
            self.assertEqual(0, result["errcode"])

    def test_customservice_close_session(self):
        with HTTMock(wechat_api_mock):
            result = self.client.customservice.close_session("openid", "test1@test")
            self.assertEqual(0, result["errcode"])

    def test_customservice_get_session(self):
        with HTTMock(wechat_api_mock):
            result = self.client.customservice.get_session("openid")
            self.assertEqual("test1@test", result["kf_account"])

    def test_customservice_get_session_list(self):
        with HTTMock(wechat_api_mock):
            result = self.client.customservice.get_session_list("test1@test")
            self.assertEqual(2, len(result))

    def test_customservice_get_wait_case(self):
        with HTTMock(wechat_api_mock):
            result = self.client.customservice.get_wait_case()
            self.assertEqual(150, result["count"])

    def test_customservice_get_records(self):
        with HTTMock(wechat_api_mock):
            result = self.client.customservice.get_records(123456789, 987654321, 1)
            self.assertEqual(2, len(result["recordlist"]))

    def test_datacube_get_user_summary(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_user_summary("2014-12-06", "2014-12-07")
            self.assertEqual(1, len(result))

    def test_datacube_get_user_cumulate(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_user_cumulate(datetime(2014, 12, 6), datetime(2014, 12, 7))
            self.assertEqual(1, len(result))

    def test_datacube_get_interface_summary(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_interface_summary("2014-12-06", "2014-12-07")
            self.assertEqual(1, len(result))

    def test_datacube_get_interface_summary_hour(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_interface_summary_hour("2014-12-06", "2014-12-07")
            self.assertEqual(1, len(result))

    def test_datacube_get_article_summary(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_article_summary("2014-12-06", "2014-12-07")
            self.assertEqual(1, len(result))

    def test_datacube_get_article_total(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_article_total("2014-12-06", "2014-12-07")
            self.assertEqual(1, len(result))

    def test_datacube_get_user_read(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_user_read("2014-12-06", "2014-12-07")
            self.assertEqual(1, len(result))

    def test_datacube_get_user_read_hour(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_user_read_hour("2014-12-06", "2014-12-07")
            self.assertEqual(1, len(result))

    def test_datacube_get_user_share(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_user_share("2014-12-06", "2014-12-07")
            self.assertEqual(2, len(result))

    def test_datacube_get_user_share_hour(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_user_share_hour("2014-12-06", "2014-12-07")
            self.assertEqual(1, len(result))

    def test_datacube_get_upstream_msg(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_upstream_msg("2014-12-06", "2014-12-07")
            self.assertEqual(1, len(result))

    def test_datacube_get_upstream_msg_hour(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_upstream_msg_hour("2014-12-06", "2014-12-07")
            self.assertEqual(1, len(result))

    def test_datacube_get_upstream_msg_week(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_upstream_msg_week("2014-12-06", "2014-12-07")
            self.assertEqual(1, len(result))

    def test_datacube_get_upstream_msg_month(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_upstream_msg_month("2014-12-06", "2014-12-07")
            self.assertEqual(1, len(result))

    def test_datacube_get_upstream_msg_dist(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_upstream_msg_dist("2014-12-06", "2014-12-07")
            self.assertEqual(1, len(result))

    def test_datacube_get_upstream_msg_dist_week(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_upstream_msg_dist_week("2014-12-06", "2014-12-07")
            self.assertEqual(1, len(result))

    def test_datacube_get_upstream_msg_dist_month(self):
        with HTTMock(wechat_api_mock):
            result = self.client.datacube.get_upstream_msg_dist_month("2014-12-06", "2014-12-07")
            self.assertEqual(1, len(result))

    def test_device_get_qrcode_url(self):
        with HTTMock(wechat_api_mock):
            qrcode_url = self.client.device.get_qrcode_url(123)
            self.assertEqual("https://we.qq.com/d/123", qrcode_url)
            qrcode_url = self.client.device.get_qrcode_url(123, {"a": "a"})
            self.assertEqual("https://we.qq.com/d/123#YT1h", qrcode_url)

    def test_jsapi_get_ticket_response(self):
        with HTTMock(wechat_api_mock):
            result = self.client.jsapi.get_ticket()
            self.assertEqual(
                "bxLdikRXVbTPdHSM05e5u5sUoXNKd8-41ZO3MhKoyN5OfkWITDGgnr2fwJ0m9E8NYzWKVZvdVtaUgWvsdshFKA",  # NOQA
                result["ticket"],
            )
            self.assertEqual(7200, result["expires_in"])

    def test_jsapi_get_jsapi_signature(self):
        noncestr = "Wm3WZYTPz0wzccnW"
        ticket = "sM4AOVdWfPE4DxkXGEs8VMCPGGVi4C3VM0P37wVUCFvkVAy_90u5h9nbSlYy3-Sl-HhTdfl2fzFy1AOcHKP7qg"  # NOQA
        timestamp = 1414587457
        url = "http://mp.weixin.qq.com?params=value"
        signature = self.client.jsapi.get_jsapi_signature(noncestr, ticket, timestamp, url)
        self.assertEqual("0f9de62fce790f9a083d5c99e95740ceb90c27ed", signature)

    def test_jsapi_get_jsapi_card_ticket(self):
        """card_ticket 与 jsapi_ticket 的 api 都相同，除了请求参数 type 为 wx_card
        所以这里使用与 `test_jsapi_get_ticket` 相同的测试文件"""
        with HTTMock(wechat_api_mock):
            ticket = self.client.jsapi.get_jsapi_card_ticket()
            self.assertEqual(
                "bxLdikRXVbTPdHSM05e5u5sUoXNKd8-41ZO3MhKoyN5OfkWITDGgnr2fwJ0m9E8NYzWKVZvdVtaUgWvsdshFKA",  # NOQA
                ticket,
            )
            self.assertTrue(7200 < self.client.session.get(f"{self.client.appid}_jsapi_card_ticket_expires_at"))
            self.assertEqual(
                self.client.session.get(f"{self.client.appid}_jsapi_card_ticket"),
                "bxLdikRXVbTPdHSM05e5u5sUoXNKd8-41ZO3MhKoyN5OfkWITDGgnr2fwJ0m9E8NYzWKVZvdVtaUgWvsdshFKA",
            )

    def test_jsapi_card_ext(self):
        card_ext = json.loads(JsApiCardExt("asdf", openid="2").to_json())
        self.assertNotIn("outer_str", card_ext)
        self.assertNotIn("code", card_ext)

        card_ext = json.loads(JsApiCardExt("asdf", code="4", openid="2").to_json())
        self.assertIn("code", card_ext)

    def test_jsapi_get_jsapi_add_card_params(self):
        """微信签名测试工具：http://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=cardsign"""
        nonce_str = "Wm3WZYTPz0wzccnW"
        card_ticket = "sM4AOVdWfPE4DxkXGEs8VMCPGGVi4C3VM0P37wVUCFvkVAy_90u5h9nbSlYy3-Sl-HhTdfl2fzFy1AOcHKP7qg"
        timestamp = "1414587457"
        card_id = "random_card_id"
        code = "random_code"
        openid = "random_openid"

        # 测试最少填写
        card_params = self.client.jsapi.get_jsapi_add_card_params(
            card_ticket=card_ticket, timestamp=timestamp, card_id=card_id, nonce_str=nonce_str
        )
        self.assertEqual(
            JsApiCardExt(
                signature="22dce6bad4db532d4a2ef82ca2ca7bbe1e10ef28",
                nonce_str=nonce_str,
                timestamp=timestamp,
            ),
            card_params,
        )
        # 测试自定义code
        card_params = self.client.jsapi.get_jsapi_add_card_params(
            card_ticket=card_ticket, timestamp=timestamp, card_id=card_id, nonce_str=nonce_str, code=code
        )
        self.assertEqual(
            JsApiCardExt(
                nonce_str=nonce_str,
                timestamp=timestamp,
                code=code,
                signature="2e9c6d12952246e071717d7baeab20c30420b5cd",
            ),
            card_params,
        )
        # 测试指定用户领取
        card_params = self.client.jsapi.get_jsapi_add_card_params(
            card_ticket=card_ticket, timestamp=timestamp, card_id=card_id, nonce_str=nonce_str, openid=openid
        )
        self.assertEqual(
            JsApiCardExt(
                nonce_str=nonce_str,
                timestamp=timestamp,
                openid=openid,
                signature="ded860a5dd4467312764bd86e544ad0579cbfad0",
            ),
            card_params,
        )
        # 测试指定用户领取且自定义code
        card_params = self.client.jsapi.get_jsapi_add_card_params(
            card_ticket=card_ticket, timestamp=timestamp, card_id=card_id, nonce_str=nonce_str, openid=openid, code=code
        )
        self.assertEqual(
            JsApiCardExt(
                nonce_str=nonce_str,
                timestamp=timestamp,
                openid=openid,
                code=code,
                signature="950dc1842852457ea573d4d6af34879c1ec093c8",
            ),
            card_params,
        )

    def test_menu_get_menu_info(self):
        with HTTMock(wechat_api_mock):
            menu_info = self.client.menu.get_menu_info()
            self.assertEqual(1, menu_info["is_menu_open"])

    def test_message_get_autoreply_info(self):
        with HTTMock(wechat_api_mock):
            autoreply = self.client.message.get_autoreply_info()
            self.assertEqual(1, autoreply["is_autoreply_open"])

    def test_shakearound_apply_device_id(self):
        with HTTMock(wechat_api_mock):
            res = self.client.shakearound.apply_device_id(1, "test")
            self.assertEqual(123, res["apply_id"])

    def test_shakearound_update_device(self):
        with HTTMock(wechat_api_mock):
            res = self.client.shakearound.update_device("1234", comment="test")
            self.assertEqual(0, res["errcode"])

    def test_shakearound_bind_device_location(self):
        with HTTMock(wechat_api_mock):
            res = self.client.shakearound.bind_device_location(123, 1234)
            self.assertEqual(0, res["errcode"])

    def test_shakearound_search_device(self):
        with HTTMock(wechat_api_mock):
            res = self.client.shakearound.search_device(apply_id=123)
            self.assertEqual(151, res["total_count"])
            self.assertEqual(2, len(res["devices"]))

    def test_shakearound_add_page(self):
        with HTTMock(wechat_api_mock):
            res = self.client.shakearound.add_page("test", "test", "http://www.qq.com", "http://www.qq.com")
            self.assertEqual(28840, res["page_id"])

    def test_shakearound_update_page(self):
        with HTTMock(wechat_api_mock):
            res = self.client.shakearound.update_page(123, "test", "test", "http://www.qq.com", "http://www.qq.com")
            self.assertEqual(28840, res["page_id"])

    def test_shakearound_delete_page(self):
        with HTTMock(wechat_api_mock):
            res = self.client.shakearound.delete_page(123)
            self.assertEqual(0, res["errcode"])

    def test_shakearound_search_page(self):
        with HTTMock(wechat_api_mock):
            res = self.client.shakearound.search_pages(123)
            self.assertEqual(2, res["total_count"])
            self.assertEqual(2, len(res["pages"]))

    def test_shakearound_add_material(self):
        with HTTMock(wechat_api_mock):
            media_file = io.StringIO("nothing")
            res = self.client.shakearound.add_material(media_file, "icon")
            self.assertEqual(
                "http://shp.qpic.cn/wechat_shakearound_pic/0/1428377032e9dd2797018cad79186e03e8c5aec8dc/120",  # NOQA
                res["pic_url"],
            )

    def test_shakearound_bind_device_pages(self):
        with HTTMock(wechat_api_mock):
            res = self.client.shakearound.bind_device_pages(123, 1, 1, 1234)
            self.assertEqual(0, res["errcode"])

    def test_shakearound_get_shake_info(self):
        with HTTMock(wechat_api_mock):
            res = self.client.shakearound.get_shake_info("123456")
            self.assertEqual(14211, res["page_id"])
            self.assertEqual("oVDmXjp7y8aG2AlBuRpMZTb1-cmA", res["openid"])

    def test_shakearound_get_device_statistics(self):
        with HTTMock(wechat_api_mock):
            res = self.client.shakearound.get_device_statistics("2015-04-01 00:00:00", "2015-04-17 00:00:00", 1234)
            self.assertEqual(2, len(res))

    def test_shakearound_get_page_statistics(self):
        with HTTMock(wechat_api_mock):
            res = self.client.shakearound.get_page_statistics("2015-04-01 00:00:00", "2015-04-17 00:00:00", 1234)
            self.assertEqual(2, len(res))

    def test_material_get_count(self):
        with HTTMock(wechat_api_mock):
            res = self.client.material.get_count()
            self.assertEqual(1, res["voice_count"])
            self.assertEqual(2, res["video_count"])
            self.assertEqual(3, res["image_count"])
            self.assertEqual(4, res["news_count"])

    def test_shakearound_get_apply_status(self):
        with HTTMock(wechat_api_mock):
            res = self.client.shakearound.get_apply_status(1234)
            self.assertEqual(4, len(res))

    def test_reraise_requests_exception(self):
        @urlmatch(netloc=r"(.*\.)?api\.weixin\.qq\.com$")
        def _wechat_api_mock(url, request):
            return {"status_code": 404, "content": "404 not found"}

        try:
            with HTTMock(_wechat_api_mock):
                self.client.material.get_count()
        except WeChatClientException as e:
            self.assertEqual(404, e.response.status_code)

    def test_wifi_list_shops(self):
        with HTTMock(wechat_api_mock):
            res = self.client.wifi.list_shops()
            self.assertEqual(16, res["totalcount"])
            self.assertEqual(1, res["pageindex"])

    def test_wifi_get_shop(self):
        with HTTMock(wechat_api_mock):
            res = self.client.wifi.get_shop(1)
            self.assertEqual(1, res["bar_type"])
            self.assertEqual(2, res["ap_count"])

    def test_wifi_add_device(self):
        with HTTMock(wechat_api_mock):
            res = self.client.wifi.add_device(123, "WX-test", "12345678", "00:1f:7a:ad:5c:a8")
            self.assertEqual(0, res["errcode"])

    def test_wifi_list_devices(self):
        with HTTMock(wechat_api_mock):
            res = self.client.wifi.list_devices()
            self.assertEqual(2, res["totalcount"])
            self.assertEqual(1, res["pageindex"])

    def test_wifi_delete_device(self):
        with HTTMock(wechat_api_mock):
            res = self.client.wifi.delete_device("00:1f:7a:ad:5c:a8")
            self.assertEqual(0, res["errcode"])

    def test_wifi_get_qrcode_url(self):
        with HTTMock(wechat_api_mock):
            qrcode_url = self.client.wifi.get_qrcode_url(123, 0)
            self.assertEqual("http://www.qq.com", qrcode_url)

    def test_wifi_set_homepage(self):
        with HTTMock(wechat_api_mock):
            res = self.client.wifi.set_homepage(123, 0)
            self.assertEqual(0, res["errcode"])

    def test_wifi_get_homepage(self):
        with HTTMock(wechat_api_mock):
            res = self.client.wifi.get_homepage(429620)
            self.assertEqual(1, res["template_id"])
            self.assertEqual("http://wifi.weixin.qq.com/", res["url"])

    def test_wifi_list_statistics(self):
        with HTTMock(wechat_api_mock):
            res = self.client.wifi.list_statistics("2015-05-01", "2015-05-02")
            self.assertEqual(2, len(res))

    def test_upload_mass_image(self):
        media_file = io.StringIO("nothing")
        with HTTMock(wechat_api_mock):
            res = self.client.media.upload_mass_image(media_file)
        self.assertEqual(
            "http://mmbiz.qpic.cn/mmbiz/gLO17UPS6FS2xsypf378iaNhWacZ1G1UplZYWEYfwvuU6Ont96b1roYs CNFwaRrSaKTPCUdBK9DgEHicsKwWCBRQ/0",  # NOQA
            res,
        )

    def test_scan_get_merchant_info(self):
        with HTTMock(wechat_api_mock):
            res = self.client.scan.get_merchant_info()
        self.assertEqual(8888, res["verified_firm_code_list"][0])

    def test_scan_create_product(self):
        with HTTMock(wechat_api_mock):
            res = self.client.scan.create_product(
                {
                    "keystandard": "ean13",
                    "keystr": "6900000000000",
                }
            )
        self.assertEqual("5g0B4A90aqc", res["pid"])

    def test_scan_publish_product(self):
        with HTTMock(wechat_api_mock):
            res = self.client.scan.publish_product("ean13", "6900873042720")
        self.assertEqual(0, res["errcode"])

    def test_scan_unpublish_product(self):
        with HTTMock(wechat_api_mock):
            res = self.client.scan.unpublish_product("ean13", "6900873042720")
        self.assertEqual(0, res["errcode"])

    def test_scan_set_test_whitelist(self):
        with HTTMock(wechat_api_mock):
            res = self.client.scan.set_test_whitelist(["openid1"], ["messense"])
        self.assertEqual(0, res["errcode"])

    def test_scan_get_product(self):
        with HTTMock(wechat_api_mock):
            res = self.client.scan.get_product("ean13", "6900873042720")
        self.assertIn("brand_info", res)

    def test_scan_list_product(self):
        with HTTMock(wechat_api_mock):
            res = self.client.scan.list_product()
        self.assertEqual(2, res["total"])

    def test_scan_update_product(self):
        with HTTMock(wechat_api_mock):
            res = self.client.scan.update_product(
                {
                    "keystandard": "ean13",
                    "keystr": "6900000000000",
                }
            )
        self.assertEqual("5g0B4A90aqc", res["pid"])

    def test_scan_clear_product(self):
        with HTTMock(wechat_api_mock):
            res = self.client.scan.clear_product("ean13", "6900873042720")
        self.assertEqual(0, res["errcode"])

    def test_scan_check_ticket(self):
        with HTTMock(wechat_api_mock):
            res = self.client.scan.check_ticket("Ym1haDlvNXJqY3Ru1")
        self.assertEqual("otAzGjrS4AYCmeJM1GhEOcHXXTAo", res["openid"])

    def test_change_openid(self):
        with HTTMock(wechat_api_mock):
            res = self.client.user.change_openid(
                "xxxxx",
                ["oEmYbwN-n24jxvk4Sox81qedINkQ", "oEmYbwH9uVd4RKJk7ZZg6SzL6tTo"],
            )
        self.assertEqual(2, len(res))
        self.assertEqual("o2FwqwI9xCsVadFah_HtpPfaR-X4", res[0]["new_openid"])
        self.assertEqual("ori_openid error", res[1]["err_msg"])

    def test_code_to_session(self):
        with HTTMock(wechat_api_mock):
            res = self.client.wxa.code_to_session("023dUeGW1oeGOZ0JXvHW1SDVFW1dUeGu")
        self.assertIn("session_key", res)
        self.assertEqual("D1ZWEygStjuLCnZ9IN2l4Q==", res["session_key"])
        self.assertEqual("o16wA0b4AZKzgVJR3MBwoUdTfU_E", res["openid"])
        self.assertEqual("or4zX05h_Ykt4ju0TUfx3CQsvfTo", res["unionid"])

    def test_get_phone_number(self):
        with HTTMock(wechat_api_mock):
            res = self.client.wxa.get_phone_number("code")
        self.assertEqual("13123456789", res["phone_info"]["purePhoneNumber"])

    def test_client_expires_at_consistency(self):
        from redis.asyncio import Redis
        from aiowechatpy.session.redisstorage import RedisStorage

        redis = Redis()
        session = RedisStorage(redis)
        client1 = WeChatClient(self.app_id, self.secret, session=session)
        client2 = WeChatClient(self.app_id, self.secret, session=session)
        assert client1.expires_at == client2.expires_at
        expires_at = time.time() + 7200
        client1.expires_at = expires_at
        assert client1.expires_at == client2.expires_at == expires_at
