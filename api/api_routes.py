from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from crud import crud
from models import models
from schemas import schemas
from models.database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/api/", response_model=schemas.API)
def create_api(api: schemas.APICreate, db: Session = Depends(get_db)):
    return crud.create_api(db=db, api=api)

@router.get("/apis/", response_model=list[schemas.API])
def read_apis(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_apis(db, skip=skip, limit=limit)

@router.get("/apis/{api_id}", response_model=schemas.API)
def read_api(api_id: int, db: Session = Depends(get_db)):
    db_api = crud.get_api(db, api_id=api_id)
    if db_api is None:
        raise HTTPException(status_code=404, detail="API not found")
    return db_api

@router.put("/apis/{api_id}", response_model=schemas.API)
def update_api(api_id: int, api: schemas.APIUpdate, db: Session = Depends(get_db)):
    db_api = crud.get_api(db, api_id=api_id)
    if db_api is None:
        raise HTTPException(status_code=404, detail="API not found")
    return crud.update_api(db=db, api_id=api_id, api=api)

@router.delete("/apis/{api_id}")
def delete_api(api_id: int, db: Session = Depends(get_db)):
    db_api = crud.get_api(db, api_id=api_id)
    if db_api is None:
        raise HTTPException(status_code=404, detail="API not found")
    crud.delete_api(db=db, api_id=api_id)
    return {"detail": "API deleted"}

@router.post("/apis/{api_id}/likes/", response_model=schemas.Like)  
def create_like(api_id: int, db: Session = Depends(get_db)):
    like = schemas.LikeCreate(api_id=api_id)
    return crud.create_like(db=db, like=like)

@router.get("/apis/{api_id}/likes/count/", response_model=int)
def get_likes_count(api_id: int, db: Session = Depends(get_db)):
    return db.query(models.Like).filter(models.Like.api_id == api_id).count()

@router.get("/likes/{like_id}", response_model=schemas.Like)
def read_like(like_id: int, db: Session = Depends(get_db)):
    db_like = db.query(models.Like).filter(models.Like.id == like_id).first()
    if db_like is None:
        raise HTTPException(status_code=404, detail="Like not found")
    return db_like



@router.post("/comments/", response_model=schemas.Comment)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    return crud.create_comment(db=db, comment=comment)

@router.get("/comments/{api_id}", response_model=list[schemas.Comment])
def read_comments(api_id: int, db: Session = Depends(get_db)):
    return crud.get_comments(db, api_id=api_id)
