# api/api_routes.py

import json
from typing import List
from fastapi import APIRouter, Body, Depends, Form, HTTPException, UploadFile, File
from sqlalchemy import func, select
from api.auth import fastapi_users, auth_backend, current_active_user
from sqlalchemy.ext.asyncio import AsyncSession
import shutil
from dependencies import get_db
from models import models
from crud import crud
from schemas import schemas

router = APIRouter()

@router.post("/apis/", response_model=schemas.API)
async def create_api(
    api_data: str = Form(...),
    image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
):
    # Parse the JSON data
    api_dict = json.loads(api_data)
    api = schemas.APICreate(**api_dict)
    
    file_location = None
    if image:
        file_location = f"static/images/{image.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        api.image = file_location

    db_api = await crud.create_api(db=db, api=api)
    return db_api

@router.get("/apis/", response_model=List[schemas.API])
async def read_apis(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await crud.get_apis(db, skip=skip, limit=limit)

@router.get("/apis/{api_id}", response_model=schemas.API)
async def read_api(api_id: int, db: AsyncSession = Depends(get_db)):
    api = await crud.get_api(db, api_id=api_id)
    if api is None:
        raise HTTPException(status_code=404, detail="API not found")
    return api

@router.put("/apis/{api_id}", response_model=schemas.API)
async def update_api(api_id: int, api: schemas.APIUpdate, db: AsyncSession = Depends(get_db)):
    db_api = await crud.get_api(db, api_id=api_id)
    if db_api is None:
        raise HTTPException(status_code=404, detail="API not found")
    return await crud.update_api(db=db, api_id=api_id, api=api)


@router.delete("/apis/{api_id}")
async def delete_api(api_id: int, db: AsyncSession = Depends(get_db)):
    db_api = await crud.get_api(db, api_id=api_id)
    if db_api is None:
        raise HTTPException(status_code=404, detail="API not found")
    await crud.delete_api(db=db, api_id=api_id)
    return {"detail": "API deleted"}

@router.post("/apis/{api_id}/likes/", response_model=schemas.Like)
async def create_like(
    api_id: int,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(current_active_user)
):
    like = schemas.LikeCreate(api_id=api_id)
    return await crud.create_like(db=db, like=like, user_id=user.id)

@router.get("/apis/{api_id}/likes/count/", response_model=int)
async def get_likes_count(api_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.count(models.Like.id)).filter(models.Like.api_id == api_id))
    return result.scalar()

@router.get("/likes/{like_id}", response_model=schemas.Like)
async def read_like(like_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Like).filter(models.Like.id == like_id))
    db_like = result.scalars().first()
    if db_like is None:
        raise HTTPException(status_code=404, detail="Like not found")
    return db_like

@router.post("/comments/", response_model=schemas.Comment)
async def create_comment(comment: schemas.CommentCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_comment(db=db, comment=comment)

@router.get("/comments/{api_id}", response_model=List[schemas.Comment])
async def read_comments(api_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_comments(db, api_id=api_id)

@router.post("/apis/{api_id}/endpoints/", response_model=schemas.Endpoint)
async def create_endpoint(
    api_id: int,
    endpoint: schemas.EndpointCreate,
    db: AsyncSession = Depends(get_db),
):
    return await crud.create_endpoint(db=db, api_id=api_id, endpoint=endpoint)

@router.get("/apis/{api_id}/endpoints/{endpoint_id}", response_model=schemas.Endpoint)
async def read_endpoint(
    api_id: int,
    endpoint_id: int,
    db: AsyncSession = Depends(get_db),
):
    endpoint = await crud.get_endpoint(db=db, endpoint_id=endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return endpoint

@router.put("/apis/{api_id}/endpoints/{endpoint_id}", response_model=schemas.Endpoint)
async def update_endpoint(
    api_id: int,
    endpoint_id: int,
    endpoint: schemas.EndpointUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_endpoint = await crud.update_endpoint(db=db, endpoint_id=endpoint_id, endpoint=endpoint)
    if not db_endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return db_endpoint

@router.delete("/apis/{api_id}/endpoints/{endpoint_id}")
async def delete_endpoint(
    api_id: int,
    endpoint_id: int,
    db: AsyncSession = Depends(get_db),
):
    db_endpoint = await crud.delete_endpoint(db=db, endpoint_id=endpoint_id)
    if not db_endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return {"detail": "Endpoint deleted"}

@router.get("/apis/random", response_model=List[schemas.API])
async def read_random_apis(db: AsyncSession = Depends(get_db), limit: int = 5):
    apis = await crud.get_apis(db)
    random_apis = random.sample(apis, min(len(apis), limit))
    return random_apis