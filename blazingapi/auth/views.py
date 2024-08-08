from blazingapi.app import app
from blazingapi.auth.decorators import login_required
from blazingapi.auth.models import User
from blazingapi.response import Response
from blazingapi.settings import settings


@app.post(settings.LOGIN_ENDPOINT)
def login(request):

    if request.user.is_authenticated:
        return Response(body=request.user, status=200)

    username = request.data["username"]
    password = request.data["password"]

    user = User.manager.get(username=username)

    if user.check_password(password):
        return Response(body=user, status=200)

    return Response(body={"error": "Invalid credentials"}, status=401)


@app.post(settings.REGISTER_ENDPOINT)
def register(request):
    user = User(username=request.data['username'], email=request.data['email'])
    user.set_password(request.data["password"])
    user.save()
    return Response(body=user, status=201)


@login_required
@app.get(settings.ME_ENDPOINT)
def me(request):
    return Response(body=request.user, status=200)
