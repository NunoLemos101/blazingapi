import secrets

import bcrypt

from blazingapi.orm.fields import VarCharField
from blazingapi.orm.models import Model


class User(Model):
    _table = 'users'
    serializable_fields = ['id', 'username', 'email', 'token']

    username = VarCharField(max_length=100, unique=True)
    email = VarCharField(max_length=100, unique=True)
    password_hash = VarCharField(max_length=60)
    token = VarCharField(max_length=100, unique=True, nullable=True)

    @property
    def is_authenticated(self):
        return True if self.id else False

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def generate_token(self, length=32):
        return secrets.token_urlsafe(length)

    def save(self):
        if not self.token:
            self.token = self.generate_token()
        super().save()


class AnonymousUser(User):

    @property
    def is_authenticated(self):
        return False

    def set_password(self, password: str):
        pass

    def check_password(self, password: str) -> bool:
        return False

    def generate_token(self, length=32):
        return None

    @classmethod
    def create_table(cls):
        pass  # Anonymous user does not have a table

    def save(self):
        pass  # Anonymous user cannot be saved to the database

    def update(self, **kwargs):
        pass  # Anonymous user cannot be updated

    def delete(self):
        pass  # Anonymous user cannot be deleted

    def serialize(self):
        return None
