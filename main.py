from blazingapi.auth.models import User
from blazingapi.orm.query import Q

r = User.manager.filter(Q(username="admin", id=1) | Q(username="root", id=1))[5:10]
#r = User.manager.filter(Q(username="admin", id=1) | Q(username="root", id=2)).filter(email="root@gmail.com")
#r = User.manager.all()[9:]
for a in r:
    pass

