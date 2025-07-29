import datetime
import decimal
import json
import re
from enum import Enum
from typing import Any, Sequence


class JDBCType(Enum):
    INT8 = "INT8"
    INT32 = "INT32"
    INT16 = "INT16"
    INT64 = "INT64"

    FLOAT32 = "FLOAT32"
    FLOAT64 = "FLOAT64"
    # Double is the same as FLOAT64. Do we need both?
    DOUBLE = "DOUBLE"

    BINARY = "BINARY"
    BOOL = "BOOL"
    STRING = "STRING"
    DECIMAL = "DECIMAL"
    NULL = "NULL"

    TIMESTAMP_NTZ = "TIMESTAMP_NTZ"
    TIMESTAMP_LTZ = "TIMESTAMP_LTZ"
    TIME = "TIME"
    DATE = "DATE"

    ARRAY = "ARRAY"
    MAP = "MAP"
    STRUCT = "STRUCT"


def map_python_type_to_jdbc_type(value: Any) -> str:  # noqa: C901
    if value is None:
        return JDBCType.NULL.value
    if isinstance(value, bool):
        return JDBCType.BOOL.value
    if isinstance(value, int):
        return JDBCType.INT64.value
    if isinstance(value, float):
        return JDBCType.FLOAT64.value
    if isinstance(value, str):
        return JDBCType.STRING.value
    if isinstance(value, bytes):
        return JDBCType.BINARY.value
    if isinstance(value, list):
        return JDBCType.ARRAY.value
    if isinstance(value, dict):
        return JDBCType.MAP.value
    if isinstance(value, tuple):
        return JDBCType.STRUCT.value
    if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
        return JDBCType.DATE.value
    if isinstance(value, datetime.datetime):
        # Simplification: all datetimes treated as TIMESTAMP_NTZ
        return JDBCType.TIMESTAMP_NTZ.value
    if isinstance(value, decimal.Decimal):
        return JDBCType.DECIMAL.value

    raise ValueError("Unsupported Python type for mapping to JDBCType")


def parse_args(query, args):
    if isinstance(args, dict):
        return parse_placeholder_args(query, args)
    return None, parse_sequence_args(args)


def format_value(v):
    if isinstance(v, str):
        return v
    try:
        return f"{json.dumps(v)}"
    except Exception:
        return str(v)


def parse_sequence_args(args: Sequence) -> dict:
    result = {}
    if args:
        for i, v in enumerate(args):
            value = format_value(v)
            result[str(i)] = {"type": map_python_type_to_jdbc_type(v), "value": value}
    return result


def parse_placeholder_args(query, args) -> (str, dict):
    result = {}
    # List to keep track of the parts of the query
    query_parts = []
    last_end = 0
    placeholders = re.finditer(r":(\w+)", query)
    for index, placeholder in enumerate(placeholders):
        name = placeholder.group(1)
        start, end = placeholder.span()
        # Append the query part before the placeholder
        query_parts.append(query[last_end:start])
        # Append '?' for the placeholder
        query_parts.append("?")
        last_end = end
        if name in args:
            value = args[name]
            result[str(index)] = {
                "value": str(value),
                "type": map_python_type_to_jdbc_type(value),
            }
    # Append the remaining part of the query after the last placeholder
    query_parts.append(query[last_end:])
    # Join all parts to form the new query
    new_query = "".join(query_parts)
    return new_query, result
