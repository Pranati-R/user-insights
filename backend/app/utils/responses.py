from typing import Any


def success(data: Any = None, message: str = "success") -> dict[str, Any]:
    return {"message": message, "data": data}

