import os

from dotenv import load_dotenv

from .logger import get_logger

load_dotenv()


def get_env(key: str, default: str, required: bool = False):
    value = os.getenv(key)
    if value is not None:
        return value
    if required:
        raise EnvironmentError(f"Missing required environment variable: '{key}'")
    get_logger().info(
        f"Environment varialbe '{key}' not found. Using default: '{default}'"
    )
    return default


SECRET_KEY = get_env("SECRET_KEY", default="supersecret")
ALGORITHM = get_env("ALGORITHM", default="HS256")
MONGO_URI = get_env("MONGO_URI", default="mongodb://localhost:27017")
ACCESS_TOKEN_EXPIRE_MINUTES = int(get_env("ACCESS_TOKEN_EXPIRE_MINUTES", default="60"))
RATE_LIMIT = get_env("RATE_LIMIT", default="20/minute")
DB_NAME = get_env("DB_NAME", default="data_transformer")

raw_transforms = get_env("DEFAULT_TRANSFORMS", default="uppercase,rename")
DEFAULT_TRANSFORMS = [t.strip() for t in raw_transforms.split(",") if t.strip()]
ADMIN_USERNAME = get_env("ADMIN_USERNAME", default="admin")
ADMIN_PASSWORD = get_env("ADMIN_PASSWORD", default="admin123")
