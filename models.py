from __future__ import annotations
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)

    urls = Mapped[list[Url]] = relationship(back_populates='author', cascade='all, delete-orphan')

    reset_tokens: Mapped[list[PasswordResetToken]] = relationship(
        back_populates='user',
        cascade='all, delete-orphan'
    )
    accessgroups = Mapped[list[AccessGroupManage]] = relationship(back_populates='author')


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
    time_of_death = Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    access_group: Mapped[AccessGroupManage | None] = relationship(back_populates='groupid')
    author: Mapped[User] = relationship(back_populates='urls')
    logs: Mapped[list[clicklogs] | None] = relationship(back_populates='author')


# Access groups section
class AccessGroupManage(Base):
    __tablename__ = 'access_groups'

    groupid: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    author: Mapped[User] = relationship(back_populates='accessgroups')
    created_at = Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )
    emails = Mapped[list[GroupMails]] = relationship(back_populates='access_group', cascade='all, delete-orphan')


class GroupMails(Base):
    __tablename__ = 'group_mails'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    emails: Mapped[str] = mapped_column(String(120), unique=False, nullable=False)
    access_group: Mapped[AccessGroupManage] = relationship(back_populates='emails')
    

class clicklogs(Base):
    __tablename__ = 'click_logs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url_id: Mapped[int] = mapped_column(ForeignKey('urls.id'), nullable=False)
    click_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

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
