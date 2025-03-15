# -*- coding: utf-8 -*-

from typing import Optional, Final, List
import random
from enum import StrEnum
from datetime import datetime
from pydantic import BaseModel

from wechatpy.pay.utils import get_external_ip, rsa_encrypt
from wechatpy.pay.api.base import BaseWeChatPayAPI


class MchTransferSceneReportInfo(BaseModel):
    """
    【商户转账场景报备信息】 各转账场景下需报备的内容，商户需要按照所属转账场景规则传参。

    Attributes:

    - info_type: :class:`str` 【信息类型】 不能超过15个字符，商户所属转账场景下的信息类型，此字段内容为固定值，需严格按照转账场景报备信息字段说明传参。
    - info_content: :class:`str` 【信息内容】 不能超过32个字符，商户所属转账场景下的信息内容，商户可按实际业务场景自定义传参，需严格按照转账场景报备信息字段说明传参。
    """

    info_type: str
    info_content: str


class MchTransferState(StrEnum):
    """商户转账结果。

    Attributes:

    - accepted: 转账已受理。
    - processing: 转账锁定资金中。如果一直停留在该状态，建议检查账户余额是否足够，如余额不足，可充值后再原单重试。
    - wait_user_confirm: 待收款用户确认，可拉起微信收款确认页面进行收款确认。
    - transfering: 转账中，可拉起微信收款确认页面再次重试确认收款。
    - success: 转账成功。
    - fail: 转账失败。
    - canceling: 商户撤销请求受理成功，该笔转账正在撤销中。
    - cancelled: 转账撤销完成。
    """
    accepted: Final[str] = 'ACCEPTED'
    processing: Final[str] = 'PROCESSING'
    wait_user_confirm: Final[str] = 'WAIT_USER_CONFIRM'
    transfering: Final[str] = 'TRANSFERING'
    success: Final[str] = 'SUCCESS'
    fail: Final[str] = 'FAIL'
    canceling: Final[str] = 'CANCELING'
    cancelled: Final[str] = 'CANCELLED'


class MchTransferResult(BaseModel):
    """商户转账结果"""
    out_bill_no: str
    transfer_bill_no: str
    create_time: str
    state: MchTransferState
    fail_reason: Optional[str] = None
    package_info: Optional[str] = None # 【跳转领取页面的package信息】 跳转微信支付收款页的package信息，APP调起用户确认收款或者JSAPI调起用户确认收款 时需要使用的参数。


class WeChatMchTransfer(BaseWeChatPayAPI):
    """
    商户转账API。

    @see: https://pay.weixin.qq.com/doc/v3/merchant/4012716434
    """
    def transfer(
        self,
        out_bill_no: str,
        scene_id: str,
        openid: str,
        amount: int,
        remark: str,
        scene_report_info_list: List[MchTransferSceneReportInfo],
        user_name: Optional[str] = None,
        notify_url: Optional[str] = None,
        user_recv_perception: Optional[str] = None
    ) -> Optional[MchTransferResult]:
        """
        商家转账接口

        :param out_bill_no: 商户系统内部的商家单号，要求此参数只能由数字、大小写字母组成，在商户系统内部唯一。
        :param scene_id: 该笔转账使用的转账场景，可前往“商户平台-产品中心-商家转账”中申请。如：1001-现金营销。
        :param openid: 用户在商户appid下的唯一标识。
        :param amount: 转账金额(分)。
        :param remark: 转账备注，用户收款时可见该备注信息，UTF8编码，最多允许32个字符。

        :param scene_report_info_list: 【转账场景报备信息】 各转账场景下需报备的内容，商户需要按照所属转账场景规则传参。

        :param user_name: 可选
        :param notify_url: 可选
        :param user_recv_perception: 可选
        :return: 转账结果

        用户收款时感知到的收款原因将根据转账场景自动展示默认内容。如有其他展示需求，可在本字段传入。
        """
        data = {
            "appid": self.appid,
            "out_bill_no": out_bill_no,
            "transfer_scene_id": scene_id,
            "openid": openid,
            "transfer_amount": amount,
            "transfer_remark": remark,
            "transfer_scene_report_infos": [i.model_dump() for i in scene_report_info_list],
        }
        if user_name is not None:
            data["check_name"] = user_name
        if notify_url is not None:
            data["notify_url"] = notify_url
        if user_recv_perception is not None:
            data["user_recv_perception"] = user_recv_perception
        res = self._post("v3/fund-app/mch-transfer/transfer-bills", data=data)
        if not res:
            return None
        return MchTransferResult.model_validate(res)

    def query(self, out_trade_no):
        """
        企业付款查询接口

        :param out_trade_no: 商户调用企业付款API时使用的商户订单号
        :return: 返回的结果数据
        """
        data = {
            "appid": self.appid,
            "partner_trade_no": out_trade_no,
        }
        return self._post("mmpaymkttransfers/gettransferinfo", data=data)

    def transfer_bankcard(self, true_name, bank_card_no, bank_code, amount, desc=None, out_trade_no=None):
        """
        企业付款到银行卡接口

        :param true_name: 开户人名称
        :param bank_card_no: 银行卡号
        :param bank_code: 银行编号
        :param amount: 付款金额，单位分
        :param desc: 付款说明
        :param out_trade_no: 可选，商户订单号，需保持唯一性，默认自动生成
        :return: 返回的结果信息
        """
        if not out_trade_no:
            now = datetime.now()
            out_trade_no = f"{self.mch_id}{now.strftime('%Y%m%d%H%M%S')}{random.randint(1000, 10000)}"
        data = {
            "mch_id": self.mch_id,
            "partner_trade_no": out_trade_no,
            "amount": amount,
            "desc": desc,
            "enc_bank_no": self._rsa_encrypt(bank_card_no),
            "enc_true_name": self._rsa_encrypt(true_name),
            "bank_code": bank_code,
        }
        return self._post("mmpaysptrans/pay_bank", data=data)

    def query_bankcard(self, out_trade_no):
        """
        企业付款查询接口

        :param out_trade_no: 商户调用企业付款API时使用的商户订单号
        :return: 返回的结果数据
        """
        data = {
            "mch_id": self.mch_id,
            "partner_trade_no": out_trade_no,
        }
        return self._post("mmpaysptrans/query_bank", data=data)

    def get_rsa_public_key(self):
        data = {
            "mch_id": self.mch_id,
            "sign_type": "MD5",
        }
        return self._post("https://fraud.mch.weixin.qq.com/risk/getpublickey", data=data)

    def _rsa_encrypt(self, data):
        if not getattr(self, "_rsa_public_key", None):
            self._rsa_public_key = self.get_rsa_public_key()["pub_key"]
        return rsa_encrypt(data, self._rsa_public_key)
