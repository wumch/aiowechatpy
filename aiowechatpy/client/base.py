# -*- coding: utf-8 -*-
import json
import time
import inspect
import logging

import httpx

from aiowechatpy.constants import WeChatErrorCode
from aiowechatpy.session import SessionStorage
from aiowechatpy.session.memorystorage import MemoryStorage
from aiowechatpy.exceptions import WeChatClientException, APILimitedException
from aiowechatpy.client.api.base import BaseWeChatAPI


logger = logging.getLogger(__name__)


def _is_api_endpoint(obj):
    return isinstance(obj, BaseWeChatAPI)


class BaseWeChatClient:
    API_BASE_URL = ""

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        api_endpoints = inspect.getmembers(self, _is_api_endpoint)
        for name, api in api_endpoints:
            api_cls = type(api)
            api = api_cls(self)
            setattr(self, name, api)
        return self

    def __init__(self, appid, session: SessionStorage = None, timeout=None, auto_retry=True):
        self._http = httpx.AsyncClient()
        self.appid = appid
        self.session: SessionStorage = session or MemoryStorage()
        self.timeout = timeout
        self.auto_retry = auto_retry

    @property
    def access_token_key(self):
        return f"{self.appid}_access_token"

    @property
    def access_token_expires_at_key(self):
        return f"{self.appid}_access_token_expires_at"

    async def get_expires_at(self):
        return await self.session.get(self.access_token_expires_at_key, None)

    # todo: async setter 实现不正确
    async def set_expires_at(self, value):
        await self.session.set(self.access_token_expires_at_key, value)

    async def _request(self, method, url_or_endpoint, **kwargs):
        if not url_or_endpoint.startswith(("http://", "https://")):
            api_base_url = kwargs.pop("api_base_url", self.API_BASE_URL)
            url = f"{api_base_url}{url_or_endpoint}"
        else:
            url = url_or_endpoint

        if "params" not in kwargs:
            kwargs["params"] = {}
        if isinstance(kwargs["params"], dict) and "access_token" not in kwargs["params"]:
            kwargs["params"]["access_token"] = self.access_token
        if isinstance(kwargs.get("data", ""), dict):
            body = json.dumps(kwargs["data"], ensure_ascii=False)
            body = body.encode("utf-8")
            kwargs["data"] = body

        kwargs["timeout"] = kwargs.get("timeout", self.timeout)
        result_processor = kwargs.pop("result_processor", None)
        res = await self._http.request(method=method, url=url, **kwargs)
        try:
            res.raise_for_status()
        except httpx.HTTPError as reqe:
            raise WeChatClientException(
                errcode=None,
                errmsg=None,
                client=self,
                request=reqe.request,
                response=res,
            )

        return await self._handle_result(res, method, url, result_processor, **kwargs)

    def _decode_result(self, res):
        try:
            result = json.loads(res.content.decode("utf-8", "ignore"), strict=False)
        except (TypeError, ValueError):
            # Return origin response object if we can not decode it as JSON
            logger.debug("Can not decode response as JSON", exc_info=True)
            return res
        return result

    async def _handle_result(self, res, method=None, url=None, result_processor=None, **kwargs):
        if not isinstance(res, dict):
            # Dirty hack around asyncio based AsyncWeChatClient
            result = self._decode_result(res)
        else:
            result = res

        if not isinstance(result, dict):
            return result

        if "base_resp" in result:
            # Different response in device APIs. Fuck tencent!
            result.update(result.pop("base_resp"))
        if "errcode" in result:
            result["errcode"] = int(result["errcode"])

        if "errcode" in result and result["errcode"] != 0:
            errcode = result["errcode"]
            errmsg = result.get("errmsg", errcode)
            if self.auto_retry and errcode in (
                WeChatErrorCode.INVALID_CREDENTIAL.value,
                WeChatErrorCode.INVALID_ACCESS_TOKEN.value,
                WeChatErrorCode.EXPIRED_ACCESS_TOKEN.value,
            ):
                logger.info("Access token expired, fetch a new one and retry request")
                await self.fetch_access_token()
                access_token = await self.session.get(self.access_token_key)
                kwargs["params"]["access_token"] = access_token
                return await self._request(method=method, url_or_endpoint=url, result_processor=result_processor, **kwargs)
            elif errcode == WeChatErrorCode.OUT_OF_API_FREQ_LIMIT.value:
                # api freq out of limit
                raise APILimitedException(errcode, errmsg, client=self, request=res.request, response=res)
            else:
                raise WeChatClientException(errcode, errmsg, client=self, request=res.request, response=res)

        return result if not result_processor else result_processor(result)

    async def get(self, url, **kwargs):
        return await self._request(method="get", url_or_endpoint=url, **kwargs)

    async def post(self, url, **kwargs):
        return await self._request(method="post", url_or_endpoint=url, **kwargs)

    async def _fetch_access_token(self, url, params):
        """The real fetch access token"""
        logger.info("Fetching access token")
        res = await self._http.get(url=url, params=params)
        try:
            res.raise_for_status()
        except httpx.HTTPError as reqe:
            raise WeChatClientException(
                errcode=None,
                errmsg=None,
                client=self,
                request=reqe.request,
                response=res,
            )
        result = res.json()
        if "errcode" in result and result["errcode"] != 0:
            raise WeChatClientException(
                result["errcode"],
                result["errmsg"],
                client=self,
                request=res.request,
                response=res,
            )

        expires_in = 7200
        if "expires_in" in result:
            expires_in = result["expires_in"]
        await self.session.set(self.access_token_key, result["access_token"], expires_in)
        self.expires_at = int(time.time()) + expires_in
        return result

    async def fetch_access_token(self):
        raise NotImplementedError()

    async def access_token(self):
        """WeChat access token"""
        access_token = await self.session.get(self.access_token_key)
        if access_token:
            if not self.expires_at:
                # user provided access_token, just return it
                return access_token

            timestamp = time.time()
            if self.expires_at - timestamp > 60:
                return access_token

        await self.fetch_access_token()
        return await self.session.get(self.access_token_key)
