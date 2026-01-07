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
