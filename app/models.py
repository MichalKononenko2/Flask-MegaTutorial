from datetime import datetime, timezone
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from flask_login import UserMixin
from hashlib import md5

followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower', sa.String(64), sa.ForeignKey('user.username'), primary_key=True),
    sa.Column('followed', sa.String(64), sa.ForeignKey('user.username'), primary_key=True)
)

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
    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.follower == username),
        secondaryjoin=(followers.c.followed == username),
        back_populates='followers'
    )
    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.followed == username),
        secondaryjoin=(followers.c.follower == username),
        back_populates='following'
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def avatar(self, size) -> str:
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user: User):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user: User):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user: User) -> bool:
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def follower_count(self) -> int:
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery()
        )
        return db.session.scalar(query)

    def following_count(self) -> int:
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery()
        )
        return db.session.scalar(query)

    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(
              sa.or_(
                Follower.id == self.id,
                Author.id == self.id
              )
            )
            .group_by(Post).
            .order_by(Post.timestamp.desc())

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

