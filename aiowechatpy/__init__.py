# -*- coding: utf-8 -*-
import logging

from aiowechatpy.client import WeChatClient  # NOQA
from aiowechatpy.component import ComponentOAuth, WeChatComponent  # NOQA
from aiowechatpy.exceptions import (
    WeChatClientException,
    WeChatException,
    WeChatOAuthException,
    WeChatPayException,
)  # NOQA
from aiowechatpy.oauth import WeChatOAuth  # NOQA
from aiowechatpy.parser import parse_message  # NOQA
from aiowechatpy.pay import WeChatPay  # NOQA
from aiowechatpy.replies import create_reply  # NOQA

__version__ = "2.0.0.alpha26"
__author__ = "messense"

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(logging.NullHandler())
