from django.conf import settings
from functools import lru_cache


DEFAULT_CONFIG = {
    'URLS': {
        'INIT': 'https://securepay.tinkoff.ru/v2/Init',
        'GET_STATE': 'https://securepay.tinkoff.ru/v2/GetState',
        'CANCEL': 'https://securepay.tinkoff.ru/v2/Cancel',
    },
    'DOLYAME': {
        'LOGIN': '',
        'PASSWORD': '',
        'CERT_PATH': '',
        'KEY_PATH': '',
        'URLS': {
            'CREATE': 'https://partner.dolyame.ru/v1/orders/create',
            'CANCEL': 'https://partner.dolyame.ru/v1/orders/{orderId}/cancel',
            'REFUND': 'https://partner.dolyame.ru/v1/orders/{orderId}/refund',
            'COMMIT': 'https://partner.dolyame.ru/v1/orders/{orderId}/commit',
            'INFO': 'https://partner.dolyame.ru/v1/orders/{orderId}/info',
            'COMPLETE_DELIVERY': 'https://partner.dolyame.ru/v1/orders/{orderId}/complete_delivery',
        }
    },
    'TAXATION': 'usn_income',
    'ITEM_TAX': 'none',
    'TERMINAL_KEY': '',
    'SECRET_KEY': '',
    'SUCCESS_URL': '',
    'FAIL_URL': '',
    'NOTIFIACTION_URL': '',
}


@lru_cache()
def get_config():
    user_config = getattr(settings, 'TINKOFF_PAYMENTS_CONFIG', {})

    config = DEFAULT_CONFIG.copy()
    config.update(user_config)

    return config
