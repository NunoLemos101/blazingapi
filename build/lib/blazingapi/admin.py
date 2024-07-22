import os

import click


@click.group()
def blazingapi_admin():
    """Command line utility for managing MyAPI."""
    pass


@blazingapi_admin.command()
@click.argument('project_name')
def startproject(project_name):
    """Create a new project with the specified name."""
    # Define the project structure with boilerplate content
    files = {
        'main.py': '''\
from framework.server import run

run()
        ''',
        'settings.py': '''\
VIEW_FILES = [
    "framework.auth.views",
    "views",
]

MODEL_FILES = [
    "framework.auth.models",
    "models"
]

MIDDLEWARE_CLASSES = [
    "framework.security.middleware.XFrameOptionsMiddleware",
    "framework.auth.middleware.BearerAuthenticationMiddleware",
]

DB_FILE = "db.sqlite3"

LOGIN_ENDPOINT = "/api/auth/login"
REGISTER_ENDPOINT = "/api/auth/register"
ME_ENDPOINT = "/api/auth/me"

X_FRAME_OPTIONS = "DENY"
''',
        'views.py': '# Define your view functions here\n\nfrom framework.app import app\nfrom framework.response import Response\n\n\n@app.get("/index")\ndef index(request):\n    return Response(body={"message": "Hello, world!"})\n',
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
