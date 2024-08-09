import os

import click


@click.group()
def blazingapi_admin():
    """
    Command line utility for managing BlazingAPI.
    """
    pass


@blazingapi_admin.command()
@click.argument('project_name')
def startproject(project_name):
    """Create a new project with the specified name."""
    # Define the project structure with boilerplate content
    files = {
        'main.py': '''\
from blazingapi.server import run

if __name__ == '__main__':
    run()
        ''',
        'settings.py': '''\
DEBUG = True

VIEW_FILES = [
    "blazingapi.auth.views",
    "views",
]

MODEL_FILES = [
    "blazingapi.auth.models",
    "models"
]

MIDDLEWARE_CLASSES = [
    "blazingapi.security.middleware.CorsMiddleware",
    "blazingapi.security.middleware.XFrameOptionsMiddleware",
    "blazingapi.auth.middleware.BearerAuthenticationMiddleware",
]

DB_FILE = "db.sqlite3"

LOGIN_ENDPOINT = "/api/auth/login"
REGISTER_ENDPOINT = "/api/auth/register"
ME_ENDPOINT = "/api/auth/me"

X_FRAME_OPTIONS = "DENY"

CORS_ALLOWED_ORIGINS = ["*"]
CORS_ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOWED_HEADERS = ["Content-Type", "Authorization"]
''',
        'views.py': '# Define your view functions here\n\nfrom blazingapi.app import app\nfrom blazingapi.response import Response\n\n\n@app.get("/index")\ndef index(request):\n    return Response(body={"message": "Hello, world!"})\n',
        'models.py': '# Define your data models here\n',
        'db.sqlite3': ''
    }

    # Create project directory
    os.makedirs(project_name, exist_ok=True)

    # Create each file in the project directory
    for filename, content in files.items():
        with open(os.path.join(project_name, filename), 'w') as f:
            f.write(content)

    click.echo(f"Project '{project_name}' created successfully.")


if __name__ == '__main__':
    blazingapi_admin()
