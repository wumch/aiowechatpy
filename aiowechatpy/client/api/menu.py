# -*- coding: utf-8 -*-


from aiowechatpy.exceptions import WeChatClientException
from aiowechatpy.client.api.base import BaseWeChatAPI


class WeChatMenu(BaseWeChatAPI):
    def get(self):
        """
        查询自定义菜单。

        详情请参考
        https://developers.weixin.qq.com/doc/offiaccount/Custom_Menus/Querying_Custom_Menus.html

        :return: 返回的 JSON 数据包

        使用示例::

            from aiowechatpy import WeChatClient

            client = WeChatClient('appid', 'secret')
            menu = client.menu.get()

        """
        try:
            return self._get("menu/get")
        except WeChatClientException as e:
            if e.errcode == 46003:
                # menu not exist
                return None
            else:
                raise e

    def create(self, menu_data):
        """
        创建自定义菜单 ::

            from aiowechatpy import WeChatClient

            client = WeChatClient("appid", "secret")
            client.menu.create({
                "button":[
                    {
                        "type":"click",
                        "name":"今日歌曲",
                        "key":"V1001_TODAY_MUSIC"
                    },
                    {
                        "type":"click",
                        "name":"歌手简介",
                        "key":"V1001_TODAY_SINGER"
                    },
                    {
                        "name":"菜单",
                        "sub_button":[
                            {
                                "type":"view",
                                "name":"搜索",
                                "url":"http://www.soso.com/"
                            },
                            {
                                "type":"view",
                                "name":"视频",
                                "url":"http://v.qq.com/"
                            },
                            {
                                "type":"click",
                                "name":"赞一下我们",
                                "key":"V1001_GOOD"
                            }
                        ]
                    }
                ]
            })

        详情请参考
        https://developers.weixin.qq.com/doc/offiaccount/Custom_Menus/Creating_Custom-Defined_Menu.html

        :param menu_data: Python 字典

        :return: 返回的 JSON 数据包
        """
        return self._post("menu/create", data=menu_data)

    def update(self, menu_data):
        """
        更新自定义菜单 ::

            from aiowechatpy import WeChatClient

            client = WeChatClient("appid", "secret")
            client.menu.update({
                "button":[
                    {
                        "type":"click",
                        "name":"今日歌曲",
                        "key":"V1001_TODAY_MUSIC"
                    },
                    {
                        "type":"click",
                        "name":"歌手简介",
                        "key":"V1001_TODAY_SINGER"
                    },
                    {
                        "name":"菜单",
                        "sub_button":[
                            {
                                "type":"view",
                                "name":"搜索",
                                "url":"http://www.soso.com/"
                            },
                            {
                                "type":"view",
                                "name":"视频",
                                "url":"http://v.qq.com/"
                            },
                            {
                                "type":"click",
                                "name":"赞一下我们",
                                "key":"V1001_GOOD"
                            }
                        ]
                    }
                ]
            })

        详情请参考
        https://developers.weixin.qq.com/doc/offiaccount/Custom_Menus/Creating_Custom-Defined_Menu.html

        :param menu_data: Python 字典

        :return: 返回的 JSON 数据包
        """
        return self.create(menu_data)

    def delete(self):
        """
        删除自定义菜单。

        详情请参考
        https://developers.weixin.qq.com/doc/offiaccount/Custom_Menus/Deleting_Custom-Defined_Menu.html

        :return: 返回的 JSON 数据包

        使用示例::

            from aiowechatpy import WeChatClient

            client = WeChatClient('appid', 'secret')
            res = client.menu.delete()

        """
        return self._get("menu/delete")

    def get_menu_info(self):
        """
        获取自定义菜单配置

        详情请参考
        https://developers.weixin.qq.com/doc/offiaccount/Custom_Menus/Getting_Custom_Menu_Configurations.html

        :return: 返回的 JSON 数据包

        使用示例::

            from aiowechatpy import WeChatClient

            client = WeChatClient('appid', 'secret')
            menu_info = client.menu.get_menu_info()

        """
        return self._get("get_current_selfmenu_info")

    def add_conditional(self, menu_data):
        """
        创建个性化菜单 ::

            from aiowechatpy import WeChatClient

            client = WeChatClient("appid", "secret")
            client.menu.add_conditional({
                "button":[
                    {
                        "type":"click",
                        "name":"今日歌曲",
                        "key":"V1001_TODAY_MUSIC"
                    },
                    {
                        "type":"click",
                        "name":"歌手简介",
                        "key":"V1001_TODAY_SINGER"
                    },
                    {
                        "name":"菜单",
                        "sub_button":[
                            {
                                "type":"view",
                                "name":"搜索",
                                "url":"http://www.soso.com/"
                            },
                            {
                                "type":"view",
                                "name":"视频",
                                "url":"http://v.qq.com/"
                            },
                            {
                                "type":"click",
                                "name":"赞一下我们",
                                "key":"V1001_GOOD"
                            }
                        ]
                    }
                ],
                "matchrule":{
                  "group_id":"2",
                  "sex":"1",
                  "country":"中国",
                  "province":"广东",
                  "city":"广州",
                  "client_platform_type":"2"
                }
            })

        详情请参考
        https://developers.weixin.qq.com/doc/offiaccount/Custom_Menus/Personalized_menu_interface.html

        :param menu_data: Python 字典

        :return: 返回的 JSON 数据包
        """
        return self._post("menu/addconditional", data=menu_data)

    def del_conditional(self, menu_id):
        """
        删除个性化菜单

        详情请参考
        https://developers.weixin.qq.com/doc/offiaccount/Custom_Menus/Personalized_menu_interface.html

        :param menu_id: 菜单ID

        :return: 返回的 JSON 数据包

        使用示例::

            from aiowechatpy import WeChatClient

            client = WeChatClient('appid', 'secret')
            res = client.menu.del_conditional('menu_id')

        """
        return self._post("menu/delconditional", data={"menuid": menu_id})

    def try_match(self, user_id):
        """
        测试个性化菜单匹配结果

        详情请参考
        https://developers.weixin.qq.com/doc/offiaccount/Custom_Menus/Personalized_menu_interface.html

        :param user_id: 可以是粉丝的OpenID，也可以是粉丝的微信号。

        :return: 该接口将返回菜单配置

        使用示例::

            from aiowechatpy import WeChatClient

            client = WeChatClient('appid', 'secret')
            res = client.menu.try_match('openid')

        """
        return self._post("menu/trymatch", data={"user_id": user_id})
