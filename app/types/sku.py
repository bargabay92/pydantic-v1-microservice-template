import re

SKU_RE = re.compile(r"^[A-Z]{3}-\d{4}$")


class Sku(str):
    """Stock keeping unit like ABC-1234 (Pydantic v1 custom type)."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str):
            raise TypeError("sku must be a string")
        value = value.strip().upper()
        if not SKU_RE.match(value):
            raise ValueError("sku must look like ABC-1234")
        return cls(value)
