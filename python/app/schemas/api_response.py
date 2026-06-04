from typing import Any


def api_success(data: Any, message: str = "OK") -> dict:
    return {"code": 0, "message": message, "data": data}
