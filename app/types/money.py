from decimal import Decimal, InvalidOperation


class Money(Decimal):
    """A non-negative amount with at most 2 decimal places (Pydantic v1 custom type)."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string", pattern=r"^\d+(\.\d{1,2})?$", examples=["19.99"])

    @classmethod
    def validate(cls, value):
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise TypeError("invalid money amount")
        if amount < 0:
            raise ValueError("money must be non-negative")
        if amount.as_tuple().exponent < -2:
            raise ValueError("money has at most 2 decimal places")
        return cls(amount)
