from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from models import models
from schemas import schemas

async def get_api(db: AsyncSession, api_id: int):
    stmt = (
        select(models.API, func.count(models.Like.id).label("likes_count"))
        .outerjoin(models.Like, models.API.id == models.Like.api_id)
        .filter(models.API.id == api_id)
        .group_by(models.API.id)
    )
    result = await db.execute(stmt)
    api = result.first()

    if api is None:
        return None

    comments_result = await db.execute(select(models.Comment).filter(models.Comment.api_id == api_id))
    comments = comments_result.scalars().all()
    comments_data = [schemas.Comment.from_orm(comment) for comment in comments]

    endpoints_result = await db.execute(select(models.Endpoint).filter(models.Endpoint.api_id == api_id))
    endpoints = endpoints_result.scalars().all()
    endpoints_data = [schemas.Endpoint.from_orm(endpoint) for endpoint in endpoints]

    return schemas.API(
        id=api[0].id,
        name=api[0].name,
        description=api[0].description,
        free=api[0].free,
        documentation=api[0].documentation,
        image=api[0].image,
        comments=comments_data,
        likes=int(api[1]),
        endpoints=endpoints_data
    )

async def get_apis(db: AsyncSession, skip: int = 0, limit: int = 10):
    stmt = (
        select(models.API, func.count(models.Like.id).label("likes_count"))
        .outerjoin(models.Like, models.API.id == models.Like.api_id)
        .group_by(models.API.id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    apis = result.all()

    apis_list = []
    for api in apis:
        endpoints_result = await db.execute(select(models.Endpoint).filter(models.Endpoint.api_id == api[0].id))
        endpoints = endpoints_result.scalars().all()
        endpoints_data = [schemas.Endpoint.from_orm(endpoint) for endpoint in endpoints]

        comments_result = await db.execute(select(models.Comment).filter(models.Comment.api_id == api[0].id))
        comments = comments_result.scalars().all()
        comments_data = [schemas.Comment.from_orm(comment) for comment in comments]

        apis_list.append(
            schemas.API(
                id=api[0].id,
                name=api[0].name,
                description=api[0].description,
                free=api[0].free,
                documentation=api[0].documentation,
                image=api[0].image,
                comments=comments_data,
                likes=int(api[1]),
                endpoints=endpoints_data
            )
        )

    return apis_list

async def create_api(db: AsyncSession, api: schemas.APICreate):
    db_api = models.API(**api.dict(exclude={"image", "endpoints"}))

    if api.image is not None:
        # Handle image storage (implementation not shown)
        pass  

    db.add(db_api)
    await db.commit()
    await db.refresh(db_api)

    for endpoint in api.endpoints:
        db_endpoint = models.Endpoint(
            url=endpoint.url,
            method=endpoint.method,
            description=endpoint.description,
            api_id=db_api.id
        )
        db.add(db_endpoint)
    
    await db.commit()
    await db.refresh(db_api)

    endpoints_result = await db.execute(select(models.Endpoint).filter(models.Endpoint.api_id == db_api.id))
    endpoints = endpoints_result.scalars().all()

    api_schema = schemas.API(
        id=db_api.id,
        name=db_api.name,
        description=db_api.description,
        free=db_api.free,
        documentation=db_api.documentation,
        image=db_api.image,
        comments=[],
        likes=0,
        endpoints=[schemas.Endpoint.from_orm(endpoint) for endpoint in endpoints]
    )

    return api_schema

async def update_api(db: AsyncSession, api_id: int, api: schemas.APIUpdate):
    stmt = select(models.API).filter(models.API.id == api_id)
    result = await db.execute(stmt)
    db_api = result.scalars().first()
    
    if db_api is None:
        return None

    for key, value in api.dict(exclude_unset=True).items():
        setattr(db_api, key, value)

    await db.commit()
    await db.refresh(db_api)

    likes_count = await db.scalar(select(func.count(models.Like.id)).filter(models.Like.api_id == db_api.id))
    endpoints_result = await db.execute(select(models.Endpoint).filter(models.Endpoint.api_id == db_api.id))
    endpoints = endpoints_result.scalars().all()
    comments_result = await db.execute(select(models.Comment).filter(models.Comment.api_id == db_api.id))
    comments = comments_result.scalars().all()

    updated_api = schemas.API(
        id=db_api.id,
        name=db_api.name,
        description=db_api.description,
        free=db_api.free,
        documentation=db_api.documentation,
        image=db_api.image,
        comments=[schemas.Comment.from_orm(comment) for comment in comments],
        likes=likes_count,
        endpoints=[schemas.Endpoint.from_orm(endpoint) for endpoint in endpoints]
    )

    return updated_api

async def create_endpoint(db: AsyncSession, api_id: int, endpoint: schemas.EndpointCreate):
    db_endpoint = models.Endpoint(
        url=endpoint.url,
        method=endpoint.method,
        description=endpoint.description,
        api_id=api_id
    )
    db.add(db_endpoint)
    await db.commit()
    await db.refresh(db_endpoint)
    return db_endpoint

async def get_endpoint(db: AsyncSession, endpoint_id: int):
    return await db.get(models.Endpoint, endpoint_id)

async def update_endpoint(db: AsyncSession, endpoint_id: int, endpoint: schemas.EndpointUpdate):
    db_endpoint = await db.get(models.Endpoint, endpoint_id)
    
    if not db_endpoint:
        return None

    for key, value in endpoint.dict(exclude_unset=True).items():
        setattr(db_endpoint, key, value)

    await db.commit()
    await db.refresh(db_endpoint)
    return db_endpoint

async def delete_endpoint(db: AsyncSession, endpoint_id: int):
    db_endpoint = await db.get(models.Endpoint, endpoint_id)
    
    if db_endpoint:
        await db.delete(db_endpoint)
        await db.commit()

    return db_endpoint

async def delete_api(db: AsyncSession, api_id: int):
    stmt = select(models.API).filter(models.API.id == api_id)
    result = await db.execute(stmt)
    db_api = result.scalars().first()
    
    if db_api:
        await db.delete(db_api)
        await db.commit()
    return db_api

async def create_like(db: AsyncSession, like: schemas.LikeCreate, user_id: int):
    existing_like = await db.execute(
        select(models.Like).filter(
            models.Like.api_id == like.api_id,
            models.Like.user_id == user_id
        )
    )
    if existing_like.scalars().first():
        raise HTTPException(status_code=400, detail="User has already liked this API")

    db_like = models.Like(api_id=like.api_id, user_id=user_id)
    db.add(db_like)
    await db.commit()
    await db.refresh(db_like)
    return db_like

async def create_comment(db: AsyncSession, comment: schemas.CommentCreate):
    db_comment = models.Comment(**comment.dict())
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment

async def get_comments(db: AsyncSession, api_id: int):
    stmt = select(models.Comment).filter(models.Comment.api_id == api_id)
    result = await db.execute(stmt)
    return result.scalars().all()
