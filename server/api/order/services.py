import hashlib
import json
import types
from uuid import UUID, uuid4

import requests

from .utils import Encoder
from .models import Payment, DolyameModel
from .settings import get_config


class PaymentHTTPException(Exception):
    pass


class MerchantAPI:
    _terminal_key = None
    _secret_key = None
    _success_url = "https://thebaza.ru/api/orders/payment/response/success"
    _fail_url = "https://thebaza.ru/api/orders/payment/response/fail"

    def __init__(self, terminal_key: str = None, secret_key: str = None):
        self._terminal_key = terminal_key
        self._secret_key = secret_key

    @property
    def secret_key(self):
        if not self._secret_key:
            self._secret_key = get_config()['SECRET_KEY']
        return self._secret_key

    @property
    def terminal_key(self):
        if not self._terminal_key:
            self._terminal_key = get_config()['TERMINAL_KEY']
        return self._terminal_key
    
    @property
    def success_url(self):
        if not self._success_url:
            self._success_url = get_config()['SUCCESS_URL']
        return self._success_url
    
    @property
    def fail_url(self):
        if not self._fail_url:
            self._fail_url = get_config()['FAIL_URL']
        return self._fail_url

    def _request(self, url: str, method: types.FunctionType, data: dict) -> requests.Response:
        url = get_config()['URLS'][url]

        data.update({
            'TerminalKey': self.terminal_key,
            'Token': self._token(data),
        })

        r = method(url, data=json.dumps(data, cls=Encoder), headers={'Content-Type': 'application/json'})

        if r.status_code != 200:
            raise PaymentHTTPException('bad status code')

        return r

    def _token(self, data: dict) -> str:
        base = [
            ['Password', self.secret_key],
        ]

        if 'TerminalKey' not in data:
            base.append(['TerminalKey', self.terminal_key])

        for k, v in data.items():
            if k in 'Token':
                continue
            if isinstance(v, bool):
                base.append([k, str(v).lower()])
            elif isinstance(v, UUID):
                base.append([k, str(v)])
            elif not isinstance(v, list) and not isinstance(v, dict):
                base.append([k, v])

        base.sort(key=lambda i: i[0])
        print(base, data)
        values = ''.join(map(lambda i: str(i[1]), base))
        
        print(values)

        m = hashlib.sha256(values.encode())
        # m.update(values.encode())
        
        token = m.hexdigest()
        print(token)
        
        return token

    @staticmethod
    def update_payment_from_response(p: Payment, response: dict) -> Payment:
        for resp_field, model_field in Payment.RESPONSE_FIELDS.items():
            if resp_field in response:
                setattr(p, model_field, response.get(resp_field))

        return p

    def token_correct(self, token: str, data: dict) -> bool:
        return token == self._token(data)

    def init(self, p: Payment) -> Payment:
        response = self._request('INIT', requests.post, {
            **p.to_json(),
            "SuccessURL": self.success_url + f"/{p.pk}",
            "FailURL": self.fail_url + f"/{p.pk}",
        }).json()
        return self.update_payment_from_response(p, response)

    def status(self, p: Payment) -> Payment:
        response = self._request('GET_STATE', requests.post, {'PaymentId': p.payment_id}).json()
        return self.update_payment_from_response(p, response)

    def cancel(self, p: Payment) -> Payment:
        response = self._request('CANCEL', requests.post, {'PaymentId': p.payment_id}).json()
        return self.update_payment_from_response(p, response)


class DeliveryAPI:
    def __init__(self) -> None:
        ...


class DolyameAPI:
    _success_url = "https://thebaza.ru/api/orders/dolyame/response/success"
    _fail_url = "https://thebaza.ru/api/orders/dolyame/response/fail"
    _notification_url = "https://thebaza.ru/api/orders/dolyame/notification"

    def __init__(self, login: str = None, password: str = None, cert_path: str = None, key_path: str = None) -> None:
        self._login = login
        self._password = password
        self._cert = (cert_path, key_path)

    @property
    def login(self):
        return self._login

    @property
    def password(self):
        return self._password

    @property
    def cert(self):
        return self._cert

    @property
    def success_url(self):
        if not self._success_url:
            self._success_url = get_config()['SUCCESS_URL']
        return self._success_url
    
    @property
    def fail_url(self):
        if not self._fail_url:
            self._fail_url = get_config()['FAIL_URL']
        return self._fail_url
    
    @property
    def notification_url(self):
        if not self._notification_url:
            self._notification_url = get_config()['NOTIFIACTION_URL']
        return self._notification_url

    def _request(self, url: str, method: types.FunctionType, data: dict, order_id: str=None) -> requests.Response:
        url = get_config()['DOLYAME']['URLS'][url]
        
        if order_id:
            url = url.format(orderId=order_id)

        r: requests.Response = method(
            url,
            data=json.dumps(data, cls=Encoder),
            headers={
                'Content-Type': 'application/json',
                'X-Correlation-ID': str(data.get('id', uuid4()))
            },
            auth=(self.login, self.password),
            cert=self.cert,
            timeout=5
        )
        
        print(r.json())

        if r.status_code != 200:
            raise PaymentHTTPException(f'Dolyame error code: {r.status_code}')

        return r

    @staticmethod
    def update_payment_from_response(p: DolyameModel, response: dict) -> DolyameModel:
        for resp_field, model_field in DolyameModel.RESPONSE_FIELDS.items():
            if resp_field in response:
                setattr(p, model_field, response.get(resp_field))

        return p

    def create(self, p: DolyameModel) -> DolyameModel:
        response = self._request('CREATE', requests.post, {
            **p.to_json(),
            "success_url": self.success_url + f"/{p.pk}",
            "fail_url": self.fail_url + f"/{p.pk}",
            "notification_url": self.notification_url + f"/{p.pk}",
        }).json()
        return self.update_payment_from_response(p, response)
    
    def commit(self, p: DolyameModel) -> DolyameModel:
        response = self._request('COMMIT', requests.post, p.to_json(), p.order.id).json()
        p.commited = True

        return self.update_payment_from_response(p, response)
        
    def info(self, p: DolyameModel) -> DolyameModel:
        response = self._request('INFO', requests.get, {}, p.order.id).json()
        return self.update_payment_from_response(p, response)
    
    def refund(self, p: DolyameModel) -> DolyameModel:
        response = self._request('REFUND', requests.post, p.to_json(), p.order.id).json()
        return self.update_payment_from_response(p, response)
    
    def cancel(self, p: DolyameModel) -> DolyameModel:
        response = self._request('CANCEL', requests.post, p.to_json(), p.order.id).json()
        return self.update_payment_from_response(p, response)

    def complete_delivery(self, p: DolyameModel) -> DolyameModel:
        response = self._request('COMPLETE_DELIVERY', requests.post, p.to_json(), p.order.id).json()
        return self.update_payment_from_response(p, response)
