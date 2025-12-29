from datetime import datetime, timezone
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from flask_login import UserMixin
from hashlib import md5

class User(UserMixin, db.Model):
    username: so.Mapped[str] = so.mapped_column(sa.String(64), primary_key=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    posts : so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author'
    )
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(280))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def avatar(self, size) -> str:
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def __repr__(self) -> str:
        return '{0}(id={1},username={2})'.format(
            self.__class__.__name__, 
            self.username
        )

class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(280))
    timestamp: so.Mapped[datetime] = so.mapped_column(
      index=True, default=lambda: datetime.now(timezone.utc)
    )
    username: so.Mapped[str] = so.mapped_column(sa.ForeignKey(User.username), index=True)
    author : so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self) -> str:
        return '{0}(id={1},timestamp={2},user_id={3})'.format(
            self.__class__.__name__,
            self.id,
            self.timestamp.isoformat(),
            self.user_id
        )

@login.user_loader
def load_user(id: str) -> Optional[User]:
    return db.session.get(User, int(id))

