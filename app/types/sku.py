import re
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

SKU_RE = re.compile(r"^[A-Z]{3}-\d{4}$")


class Sku(str):
    """Stock keeping unit like ABC-1234."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str):
            raise ValueError("sku must be a string")
        value = value.strip().upper()
        if not SKU_RE.match(value):
            raise ValueError("sku must look like ABC-1234")
        return cls(value)
