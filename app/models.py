from datetime import datetime, timezone, time, timedelta
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa
import sqlalchemy.orm as so
import jwt
from app import app, db, login
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

    def follow(self, user: 'User'):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user: 'User'):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user: 'User') -> bool:
        query = self.following.select().where(User.username == user.username)
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
        return sa.select(Post).\
            join(Post.author.of_type(Author)).\
            join(Author.followers.of_type(Follower), isouter=True).\
            where(
                sa.or_(
                Follower.username == self.username,
                Author.username == self.username
                )
            ).\
            group_by(Post).\
            order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=timedelta(minutes=10)):
        return jwt.encode(
            {'reset_password': self.username, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256'
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, username)

    def __eq__(self, other: 'User') -> bool:
        return hash(self) == hash(other)

    def __hash__(self) -> int:
        return hash(self.username)

    def __repr__(self) -> str:
        return '{0}(username={1})'.format(
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

    def __eq__(self, other: 'Post') -> bool:
        return hash(self) == hash(other)

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return '{0}(id={1},user={2},timestamp={3})'.format(
            self.__class__.__name__,
            self.id,
            self.username,
            self.timestamp.isoformat()
        )

@login.user_loader
def load_user(username: str) -> Optional[User]:
    return db.session.get(User, username)

