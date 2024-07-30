import string
import random

from blazingapi.orm.models import Model
from blazingapi.orm.fields import VarCharField, TextField, ForeignKeyField
from blazingapi.auth.models import User


def random_string(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


class Book(Model):

    title = VarCharField(max_length=255)


class Article(Model):

    title = VarCharField(max_length=255)
    content = TextField()
    book = ForeignKeyField(Book)


Article.create_table()
Book.create_table()

book1 = Book.manager.all()[0]
article1 = Article(title=random_string(10), content=random_string(100), book=book1)
article1.save()

book2 = Book(title=random_string(10))
article2 = Article(title=random_string(10), content=random_string(100), book=book2)
article2.save()

articles = Article.manager.all()

article = articles[0]
print(article.title)
article.update(title="OLA")
