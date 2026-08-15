from __future__ import annotations
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)

    urls = Mapped[list[Url]] | None = relationship(back_populates='author', cascade='all, delete-orphan')

    reset_tokens: Mapped[list[PasswordResetToken]] = relationship(
        back_populates='user',
        cascade='all, delete-orphan'
    )
    access_groups = Mapped[list[AccessGroupManage]] | None = relationship(back_populates='author', cascade='all, delete-orphan')


class Url(Base):
    __tablename__ = 'urls'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    long_url: Mapped[str] = mapped_column(String(2000), nullable=False)
    short_url: Mapped[str] = mapped_column(String(50), nullable=False)
    purpose: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        default=None
    )
    rate_limit: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )
    expires_at = Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    access_group: Mapped[AccessGroupManage | None ] = relationship(back_populates='id')
    author: Mapped[User] = relationship(back_populates='urls')
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False,
        index=True,
    ) 
    access_group_id: Mapped[int] = mapped_column(
        ForeignKey('access_groups.id'),
        nullable=False,
        index=True
    )

# Access groups section
class AccessGroupManage(Base):
    __tablename__ = 'access_groups'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    group_name: Mapped[str] = mapped_column(String(50))
    author: Mapped[User] = relationship(back_populates='access_groups')
    created_at = Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )
    expires_at = Mapped[datetime] = mapped_column(
        DateTime(timezone=UTC),
        nullable=False
    )
    emails = Mapped[list[AccessMails] | None] = relationship(back_populates='access_group', cascade='all, delete-orphan')
    user_id = Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False,
        index=True
    )

class AccessLog(Base):
    __tablename__ = "access_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=False, nullable=False)
    access_group_id: Mapped[int] = mapped_column(ForeignKey('access_groups.id'), nullable=False)
    access_status: Mapped[str] = mapped_column(String, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

class AccessMails(Base):
    __tablename__ = 'access_mails'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=False, nullable=False)
    access_group: Mapped[AccessGroupManage] = relationship(back_populates='emails')
    status: Mapped[bool] = mapped_column(default=True)
    updated_at: Mapped[datetime]
    access_group_id: Mapped[int] = mapped_column(ForeignKey('access_group.id'), nullable=False)
    
class ClickLogs(Base):
    __tablename__ = 'click_logs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url_id: Mapped[int] = mapped_column(ForeignKey('urls.id'), nullable=False)
    click_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )
    method: Mapped[str] = mapped_column(String(45), nullable=False)

class PasswordResetToken(Base):
    __tablename__ = 'password_reset_token'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    user: Mapped[User] = relationship(back_populates='reset_token')
