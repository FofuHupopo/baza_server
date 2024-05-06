import decimal
import json
from uuid import UUID


class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, UUID):
            return o.hex
        return super().default(o)
