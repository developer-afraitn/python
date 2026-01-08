import re
from typing import List

import requests
import time

from app.storage.repo.apiLogRepo import ApiLogRepo
from app.utils.PersianLettersNumber import PersianLettersNumber


def http_request(
    url: str,
    method: str = "GET",
    params: dict | None = None,
    data: dict | None = None,
    headers: dict | None = None,
    timeout: int = 10,
):
    start_time = time.perf_counter()

    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=timeout
        )

        parsed_response = (
            response.json()
            if "application/json" in response.headers.get("Content-Type", "")
            else {"raw": response.text}
        )

        status_code = response.status_code

    except requests.exceptions.RequestException as e:
        parsed_response = {"error": str(e)}
        status_code = None

    duration_ms = int((time.perf_counter() - start_time) * 1000)

    # ذخیره لاگ در DB
    api_log_repo = ApiLogRepo()
    api_log_repo.create(
        method=method.upper(),
        url=url,
        params=params,
        request_body=data,
        headers=headers,
        status_code=status_code,
        response=parsed_response,
        duration_ms=duration_ms,
    )

    return {
        "status_code": status_code,
        "response": parsed_response,
        "duration_ms": duration_ms
    }

def currency_price(price, show_letter=False, show_label=True):
    if int(price):
        price = round(price / 10)

        if show_letter:
            price = PersianLettersNumber(price).persian_money()
        else:
            price = format(price,',')

        if show_label:
            price = f"{price} تومان"

        return price

    return None

def wrap_words(text: str, words: List[str], label: str) -> str:
    # حذف تکراری‌ها با حفظ ترتیب
    words = list(dict.fromkeys(words))

    escaped_words = list(map(re.escape, words))

    # الگو:
    # 1) کلمه جزئی از [label(...)] نباشد  ← negative lookbehind
    # 2) خود کلمه match شود
    pattern = rf'(?<!\[{label}\()({"|".join(escaped_words)})\b'

    return re.sub(pattern, rf'[{label}(\1)]', text)


def mask_bracketed(text: str):
    mapping = {}
    counter = 0

    def replacer(match):
        nonlocal counter
        counter += 1
        key = f"__BRACKETED{counter}__"
        mapping[key] = match.group(1)
        return key

    new_text = re.sub(r'\[([^\]]+)\]', replacer, text)
    return new_text, mapping

def unmask_bracketed(text: str, mapping: dict):
    for key, value in mapping.items():
        pattern = re.compile(re.escape(key), re.IGNORECASE)
        text = pattern.sub(f"[{value}]", text)
    return text