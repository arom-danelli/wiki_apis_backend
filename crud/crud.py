from sqlalchemy import func
from sqlalchemy.orm import Session
from models import models
from schemas import schemas

# CRUD for APIs
def get_api(db: Session, api_id: int):
    db_api = db.query(models.API).filter(models.API.id == api_id).first()
    if db_api is None:
        return None

    likes_count = db.query(models.Like).filter(models.Like.api_id == api_id).count()

    api = schemas.API.from_orm(db_api)  # create the pydantic object
    api.likes = likes_count  # set the likes
    api.comments = [schemas.Comment.from_orm(comment) for comment in db_api.comments]
    return api


def get_apis(db: Session, skip: int = 0, limit: int = 10):
    apis = db.query(models.API, func.count(models.Like.id).label('likes_count'))\
        .outerjoin(models.Like, models.API.id == models.Like.api_id)\
        .group_by(models.API)\
        .offset(skip)\
        .limit(limit)\
        .all()

    return [schemas.API(**api[0].__dict__, likes=api[1]) for api in apis]

    

def create_api(db: Session, api: schemas.APICreate):
    db_api = models.API(**api.dict())
    db.add(db_api)
    db.commit()
    db.refresh(db_api)
    return db_api

def update_api(db: Session, api_id: int, api: schemas.APIUpdate):
    db_api = db.query(models.API).filter(models.API.id == api_id).first()
    for key, value in api.dict().items():
        setattr(db_api, key, value)
    db.commit()
    db.refresh(db_api)
    return db_api

def delete_api(db: Session, api_id: int):
    db_api = db.query(models.API).filter(models.API.id == api_id).first()
    db.delete(db_api)
    db.commit()
    return db_api

# CRUD for Likes
def create_like(db: Session, like: schemas.LikeCreate):
    db_like = models.Like(**like.dict())
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return db_like  # Return the created Like object


# CRUD for Comments
def create_comment(db: Session, comment: schemas.CommentCreate):
    db_comment = models.Comment(**comment.dict())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments(db: Session, api_id: int):
    return db.query(models.Comment).filter(models.Comment.api_id == api_id).all()
