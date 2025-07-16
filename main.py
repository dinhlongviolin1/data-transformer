from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src.config import DB_NAME, MONGO_URI
from src.db import create_admin_user_if_none
from src.logger import get_logger
from src.routes import auth_router, root_router, transform_router
from src.transformer import TransformerRegistry, register_builtin_transformers


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    app.state.db = mongo_client[DB_NAME]
    get_logger().info("MongoDB connected")

    registry = TransformerRegistry()
    register_builtin_transformers(registry)
    app.state.registry = registry
    get_logger().info("Transformer Registry loaded")

    # Create admin user if none exists
    await create_admin_user_if_none(app.state.db)

    yield

    mongo_client.close()
    get_logger().info("MongoDB disconnected")


app = FastAPI(lifespan=lifespan)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


# Register routers
app.include_router(root_router)
app.include_router(auth_router)
app.include_router(transform_router)
