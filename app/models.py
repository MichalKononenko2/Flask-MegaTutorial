from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    posts : so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author'
    )

    def __repr__(self) -> str:
        return '{0}(id={1},username={2})'.format(
            self.__class__.__name__, 
            self.id,
            self.username
        )

class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(280))
    timestamp: so.Mapped[datetime] = so.mapped_column(
      index=True, default=lambda: datetime.now(timezone.utc)
    )
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    author : so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self) -> str:
        return '{0}(id={1},timestamp={2},user_id={3})'.format(
            self.__class__.__name__,
            self.id,
            self.timestamp.isoformat(),
            self.user_id
        )

