import unittest
from blazingapi.orm.validators import EmailValidator

class TestEmailValidator(unittest.TestCase):
    def setUp(self):
        self.validator = EmailValidator()

    def test_valid_emails(self):
        valid_emails = [
            "test@example.com",
            "user.name+tag+sorting@example.com",
            "user.name@subdomain.example.com",
            "user_name@example.co.in",
            "user-name@example.co.uk",
            "x@example.com",
            "example-indeed@strange-example.com"
        ]
        for email in valid_emails:
            with self.subTest(email=email):
                try:
                    self.validator(email)
                except ValueError:
                    self.fail(f"validator raised ValueError unexpectedly for email: {email}")

    def test_invalid_emails(self):
        invalid_emails = [
            "plainaddress",
            "@missingusername.com",
            "username@.com",
            "username@.com.",
            "username@com",
            "username@-example.com",
            "username@.com.com",
            "username@example..com"
        ]
        for email in invalid_emails:
            with self.subTest(email=email):
                with self.assertRaises(ValueError):
                    self.validator(email)

    def test_empty_value(self):
        with self.assertRaises(ValueError):
            self.validator("")


if __name__ == '__main__':
    unittest.main()
