"""Encode and decode Proto-Ring compatibility structured values."""

from __future__ import annotations

import re
from typing import Any

_INTEGER = re.compile(r"(?:0|-?[1-9][0-9]*)\Z")


class StructuredValueError(ValueError):
    """A local value cannot cross the strict structured-value boundary."""


def encode(value: object) -> dict[str, Any]:
    if value is None:
        return {"type": "null", "value": None}
    if type(value) is bool:
        return {"type": "boolean", "value": value}
    if type(value) is int:
        return {"type": "integer", "value": str(value)}
    if type(value) is str:
        return {"type": "string", "value": value}
    if type(value) is list:
        return {"type": "sequence", "value": [encode(item) for item in value]}
    if type(value) is dict:
        if not all(type(key) is str for key in value):
            raise StructuredValueError("structured record keys must be strings")
        return {
            "type": "record",
            "value": [
                {"name": key, "value": encode(value[key])} for key in sorted(value)
            ],
        }
    raise StructuredValueError(
        f"unsupported structured value type: {type(value).__name__}"
    )


def decode(value: object) -> object:
    if not isinstance(value, dict) or set(value) != {"type", "value"}:
        raise StructuredValueError("structured value is malformed")
    tag, payload = value["type"], value["value"]
    if tag == "null" and payload is None:
        return None
    if tag == "boolean" and type(payload) is bool:
        return payload
    if tag == "integer" and isinstance(payload, str) and _INTEGER.fullmatch(payload):
        return int(payload)
    if tag == "string" and isinstance(payload, str):
        return payload
    if tag == "sequence" and isinstance(payload, list):
        return [decode(item) for item in payload]
    if tag == "record" and isinstance(payload, list):
        output: dict[str, object] = {}
        for entry in payload:
            if (
                not isinstance(entry, dict)
                or set(entry) != {"name", "value"}
                or not isinstance(entry["name"], str)
            ):
                raise StructuredValueError("structured record entry is malformed")
            if entry["name"] in output:
                raise StructuredValueError("structured record has duplicate names")
            output[entry["name"]] = decode(entry["value"])
        return output
    raise StructuredValueError("structured value has an invalid tag or payload")
