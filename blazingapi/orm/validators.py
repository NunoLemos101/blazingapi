import re
from datetime import datetime


class BaseValidator:
    """
    Base class for all validators. Subclasses must implement the `__call__` method.
    """
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement the `__call__` method.")


class EmailValidator(BaseValidator):
    """
    Validator for email addresses. Raises a `ValueError` if the email address is invalid.
    """
    email_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{|}~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{|}~0-9A-Z]+)*"
        r'|^"([]!#-[^-~ \t]|(\\[\t -~]))+")@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE
    )

    def __call__(self, value):
        if value and not self.email_regex.match(value):
            raise ValueError(f"Invalid email address: {value}")


class ChoiceValidator(BaseValidator):
    """
    Validator for choices. Raises a `ValueError` if the value is not in the list of choices.
    """

    def __init__(self, choices):
        self.choices = choices

    def __call__(self, value):
        if value is not None and value not in self.choices:
            raise ValueError(f"Invalid choice: {value}")


class RegexValidator(BaseValidator):
    """
    Validator for regular expressions. Raises a `ValueError` if the value does not match the pattern.
    """

    def __init__(self, pattern):
        self.pattern = re.compile(pattern)

    def __call__(self, value):
        if value and not self.pattern.match(value):
            raise ValueError(f"Value does not match pattern: {value}")


class MaxValueValidator(BaseValidator):
    """
    Validator for maximum values. Raises a `ValueError` if the value exceeds the maximum value.
    """

    def __init__(self, max_value):
        self.max_value = max_value

    def __call__(self, value):
        if value is not None and value > self.max_value:
            raise ValueError(f"Value {value} exceeds maximum value of {self.max_value}")


class MinValueValidator(BaseValidator):
    """
    Validator for minimum values. Raises a `ValueError` if the value is less than the minimum value.
    """

    def __init__(self, min_value):
        self.min_value = min_value

    def __call__(self, value):
        if value is not None and value < self.min_value:
            raise ValueError(f"Value {value} is less than minimum value of {self.min_value}")


class PositiveNumberValidator(BaseValidator):
    """
    Validator for positive numbers. Raises a `ValueError` if the value is not a positive number.
    """

    def __call__(self, value):
        if value is not None and value <= 0:
            raise ValueError(f"Value {value} must be a positive number")


class NegativeNumberValidator(BaseValidator):
    """
    Validator for negative numbers. Raises a `ValueError` if the value is not a negative number.
    """
    def __call__(self, value):
        if value is not None and value >= 0:
            raise ValueError(f"Value {value} must be a negative number")


class DateTimeValidator(BaseValidator):
    """
    Validator for date and time values. Raises a `ValueError` if the value is not a valid date and time.
    """

    def __call__(self, value):
        if value is not None and not isinstance(value, datetime):
            raise ValueError(f"Value {value} is not a valid date and time")
