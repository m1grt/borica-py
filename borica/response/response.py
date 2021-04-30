# -*- coding: utf-8 -*-
import os
import uuid
import borica
import binascii
from typing import Any
from OpenSSL import crypto
from borica.config import CONFIG_DICT
from borica.base import BoricaSignMixin
from borica.response.fields import sign_fields


class BoResponse(BoricaSignMixin):
    """Base response verification.
    Dynamic class attributes set by `__seattr__` method are:
        'rc', 'eci', 'rrn', 'card', 'lang', 'nonce', 'order', 'action',
        'amount', 'p_sign', 'trtype', 'int_ref', 'approval', 'currency',
        'terminal', 'statusmsg', 'timestamp', 'tran_date', 'card_brand',
        'pares_status', 'auth_step_res', 'cardholderinfo'
    """

    def __init__(self, data):
        self.raw_data = data
        self.message = self.generate_sign_data()

    def __setattr__(self, name: str, value: Any) -> None:
        keys = []
        if name == 'raw_data' and isinstance(value, dict):

            for k, v in value.items():
                keys.append(k.lower())
                self.__dict__[k.lower()] = v
        else:
            self.__dict__[name] = value or self.raw_data.get(name.upper(), value)

    def get_is_verified(self):
        with open(CONFIG_DICT['DEV_APGW_PEM'], 'rb') as cf:
            cert_data = cf.read()
            pkey = crypto.load_publickey(crypto.FILETYPE_PEM, cert_data)
        x509 = crypto.X509()
        x509.set_pubkey(pkey)
        binary_string = binascii.unhexlify(self.p_sign)
        try:
            crypto.verify(x509, binary_string, self.message, "sha256")
            return True
        except:
            return False
