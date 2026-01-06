
from __future__ import annotations

import requests

def http_request(
    url: str,
    method: str = "GET",
    params: dict | None = None,
    data: dict | None = None,
    headers: dict | None = None,
    timeout: int = 10,
):
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            params=params,   # معمولاً برای GET
            json=data,       # معمولاً برای POST / PUT
            headers=headers,
            timeout=timeout
        )

        return {
            "status_code": response.status_code,
            "response": (
                response.json()
                if "application/json" in response.headers.get("Content-Type", "")
                else response.text
            )
        }

    except requests.exceptions.RequestException as e:
        return {
            "status_code": None,
            "response": str(e)
        }




