import json
import difflib
from uuid import UUID
from django.conf import settings
from functools import lru_cache


API_STATIC_PATH = settings.BASE_DIR / "api/static/"
COUNTRIES = json.load(open(API_STATIC_PATH / "json/countries.json", "r", encoding="utf-8"))
BASE_COUNTRIES = json.load(open(API_STATIC_PATH / "json/base_countries.json", "r", encoding="utf-8"))


def sort_by_similarity(original, strings):
    ratios = [(string, difflib.SequenceMatcher(None, original, string).ratio()) for string in strings]
    sorted_strings = sorted(ratios, key=lambda x: x[1], reverse=True)
    sorted_strings = [
        string
        for string, coincidence in sorted_strings
        if coincidence > 0
    ]

    return sorted_strings


@lru_cache
def get_country_phone_code(query: str, limit: int=5):
    if not query:
        return BASE_COUNTRIES
    
    if "+" not in query:
        query = f"+{query}"

    return sorted(
        list(filter(lambda country: country["phone_code"].startswith(query), COUNTRIES)),
        key=lambda country: (len(country["phone_code"]) - len(query), country["name_ru"])
    )[:limit]


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return obj.hex
        return json.JSONEncoder.default(self, obj)
