from numpy import sort
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Path, Request

from ..auth import admin_required, get_optional_user
from ..db import get_user, get_user_allowed_transforms, set_user_transforms
from ..models import TransformConfig, TransformRequest
from ..utils import get_db, get_registry

router = APIRouter(prefix="/transform", tags=["Transform"])


@router.post("/")
async def transform_data(
    request_data: TransformRequest,
    request: Request,
    request_user=Depends(get_optional_user),
):
    db = get_db(request)
    registry = get_registry(request)

    username = request_user.username if request_user else None
    allowed = await get_user_allowed_transforms(db, username)

    df = pd.DataFrame(request_data.data)

    for step in request_data.pipeline:
        name, *args = step.split(":")
        if allowed is not None and name not in allowed:
            raise HTTPException(status_code=403, detail=f"Not allowed: {name}")
        transformer = registry.get(name)
        if not transformer:
            raise HTTPException(status_code=400, detail=f"Unknown transformer: {name}")

        kwargs = eval(":".join(args)) if args else {}
        df = transformer(df, **kwargs)
    return {"result": df.to_dict(orient="records")}


@router.get("/")
async def get_available_transforms(
    request: Request, request_user=Depends(get_optional_user)
):
    registry = get_registry(request)
    db = get_db(request)

    username = request_user.username if request_user else None
    allowed = await get_user_allowed_transforms(db, username)

    all_transforms = sorted(registry.list_available())

    return {
        t: {
            "enabled": allowed is None or t in allowed,
            **registry.get(t).get_metadata(),
        }
        for t in all_transforms
    }


@router.put("/user/{username}")
async def set_user_transform_config(
    request: Request,
    config: TransformConfig,
    username: str = Path(..., description="Username"),
    admin=Depends(admin_required),
):
    db = get_db(request)
    registry = get_registry(request)

    available = registry.list_available()
    if invalid := [t for t in config.enabled_transforms if t not in available]:
        raise HTTPException(status_code=400, detail=f"Invalid transforms: {invalid}")

    user = await get_user(db, username)
    if user is None:
        raise HTTPException(status_code=400, detail=f"User '{username}' not found")

    await set_user_transforms(db, username, config.enabled_transforms)
    return {"status": "Updated"}
