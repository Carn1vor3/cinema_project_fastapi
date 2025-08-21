import enum
from datetime import datetime, UTC

from sqlalchemy import String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database import Base
from models.base import user_favorites
from models.carts import Carts
from models.movies import Movies, MovieRating


class GenderEnum(enum.Enum):
    MAN = "man"
    WOMAN = "woman"


class UserGroupEnum(enum.Enum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class UserGroup(Base):
    __tablename__ = "user_group"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[UserGroupEnum] = mapped_column(
        Enum(UserGroupEnum), nullable=False, unique=True
    )

    users: Mapped[list["User"]] = relationship("User", back_populates="group")


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
    group_id: Mapped[int] = mapped_column(ForeignKey("user_group.id"), nullable=False)
    group: Mapped["UserGroup"] = relationship("UserGroup", back_populates="users")
    user_profile: Mapped["UserProfile"] = relationship(
        "UserProfile", back_populates="user", uselist=False
    )

    activation_token: Mapped["ActivationToken"] = relationship(
        "ActivationToken", back_populates="user", uselist=False
    )
    password_reset_token: Mapped["PasswordResetToken"] = relationship(
        "PasswordResetToken", back_populates="user", uselist=False
    )
    refresh_token: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user"
    )
    favorite_movies: Mapped[list["Movies"]] = relationship(
        "Movies", secondary=user_favorites, back_populates="favorited_by"
    )
    ratings: Mapped[list["MovieRating"]] = relationship(
        "MovieRating", back_populates="user"
    )
    carts: Mapped["Carts"] = relationship("Carts", back_populates="user", uselist=False)


class UserProfile(Base):
    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="user_profile")

    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)

    gender: Mapped[GenderEnum] = mapped_column(Enum(GenderEnum), nullable=True)
    date_of_birth: Mapped[datetime] = mapped_column(nullable=True)
    info: Mapped[str] = mapped_column(nullable=True)


class ActivationToken(Base):
    __tablename__ = "activation_token"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), unique=True, nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="activation_token")
    token: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class PasswordResetToken(Base):
    __tablename__ = "password_reset_token"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), unique=True, nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="password_reset_token")
    token: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="refresh_token")

    token: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
