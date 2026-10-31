from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Post
from app.schemas import PostCreate, PostUpdate


def create_post(db: Session, data: PostCreate) -> Post:
    post = Post(
        title=data.title,
        content=data.content,
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post

def get_post(db: Session, post_id: int) -> Post | None:
    return db.get(Post, post_id)


def list_posts(db: Session) -> list[Post]:
    return list(db.scalars(select(Post).order_by(Post.id.desc())).all())


def update_post(db: Session, post_id: int, data: PostUpdate) -> Post | None:
    post = db.get(Post, post_id)
    if post is None:
        return None

    # exclude_unset=True — меняем только то, что клиент реально прислал
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)
    return post

def delete_post(db: Session, post_id: int) -> bool:
    post = db.get(Post, post_id)
    if post is None:
        return False
    db.delete(post)
    db.commit()
    return True
