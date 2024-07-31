import re


class BaseValidator:

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement the `__call__` method.")


class EmailValidator:
    email_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{|}~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{|}~0-9A-Z]+)*"
        r'|^"([]!#-[^-~ \t]|(\\[\t -~]))+")@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE
    )

    def __call__(self, value):
        if value and not self.email_regex.match(value):
            raise ValueError(f"Invalid email address: {value}")
