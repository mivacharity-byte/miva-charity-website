
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import News
from schemas.news import NewsCreate, NewsResponse, NewsUpdate
from security import require_admin


router = APIRouter(
    prefix="/api/news",
    tags=["News"],
)


@router.get("/", response_model=list[NewsResponse])
def list_news(
    db: Session = Depends(get_db),
):
    statement = (
        select(News)
        .where(News.status == "published")
        .order_by(News.published_at.desc(), News.id.desc())
    )

    return db.scalars(statement).all()


@router.get("/{news_id}", response_model=NewsResponse)
def get_news(
    news_id: int,
    db: Session = Depends(get_db),
):
    article = db.get(News, news_id)

    if article is None or article.status != "published":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News article not found",
        )

    return article


@router.post(
    "/",
    response_model=NewsResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_news(
    news_data: NewsCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    article_data = news_data.model_dump()
    article_status = article_data["status"]

    article = News(
        **article_data,
        author_id=current_admin.id,
        published_at=(
            datetime.now(timezone.utc)
            if article_status == "published"
            else None
        ),
    )

    db.add(article)
    db.commit()
    db.refresh(article)

    return article


@router.patch("/{news_id}", response_model=NewsResponse)
def update_news(
    news_id: int,
    news_data: NewsUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    article = db.get(News, news_id)

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News article not found",
        )

    updates = news_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(article, field, value)

    if "status" in updates:
        if article.status == "published" and article.published_at is None:
            article.published_at = datetime.now(timezone.utc)
        elif article.status == "draft":
            article.published_at = None

    db.commit()
    db.refresh(article)

    return article


@router.delete(
    "/{news_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_news(
    news_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    article = db.get(News, news_id)

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News article not found",
        )

    db.delete(article)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
