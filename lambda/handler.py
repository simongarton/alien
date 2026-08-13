"""Lambda handler for the alien-generator API.

Wraps the existing generate_alien / paint_image / alien_json_to_text
functions with an HTTP handler that reads generation parameters from the
API Gateway query string, defaulting anything that isn't supplied.
"""

import base64
from typing import Any

from alien_generator import generate_alien
from alien_json_to_text import alien_json_to_text
from image_painter import paint_image

TRUE_VALUES = {"1", "true", "yes"}


def _int_param(params: dict[str, str], name: str, default: int | None) -> int | None:
    value = params.get(name)
    return int(value) if value is not None else default


def _bool_param(params: dict[str, str], name: str, default: bool) -> bool:
    value = params.get(name)
    return value.lower() in TRUE_VALUES if value is not None else default


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    params: dict[str, str] = event.get("queryStringParameters") or {}
    fmt = params.get("format", "png").lower()

    if fmt not in ("png", "text"):
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "text/plain"},
            "body": f"Unknown format '{fmt}', expected 'png' or 'text'",
        }

    alien = generate_alien(
        width=_int_param(params, "width", 16),
        height=_int_param(params, "height", 16),
        background=params.get("background", "#ffffff"),
        palette=params.get("palette", "cga"),
        eyes=_int_param(params, "eyes", 2),
        bigeyes=_bool_param(params, "bigeyes", False),
        legs=_int_param(params, "legs", None),
        arms=_int_param(params, "arms", 0),
        shape=params.get("shape"),
    )

    if fmt == "text":
        body = "\n".join(alien_json_to_text(alien))
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/plain"},
            "body": body,
        }

    path = paint_image(data=alien, filename="/tmp/alien.png", scale=20)
    with open(path, "rb") as f:
        image_bytes = f.read()

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "image/png"},
        "isBase64Encoded": True,
        "body": base64.b64encode(image_bytes).decode("ascii"),
    }
