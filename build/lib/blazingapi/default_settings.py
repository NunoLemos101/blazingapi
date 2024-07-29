
VIEW_FILES = [
    "blazingapi.auth.views",
    "views",
]

MODEL_FILES = [
    "blazingapi.auth.models",
    "models"
]

MIDDLEWARE_CLASSES = [
    "blazingapi.security.middleware.XFrameOptionsMiddleware",
    "blazingapi.auth.middleware.BearerAuthenticationMiddleware",
]

DB_FILE = "db.sqlite3"

LOGIN_ENDPOINT = "/api/auth/login"
REGISTER_ENDPOINT = "/api/auth/register"
ME_ENDPOINT = "/api/auth/me"

X_FRAME_OPTIONS = "DENY"
