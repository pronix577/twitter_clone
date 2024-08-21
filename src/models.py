from __future__ import annotations

import re
from datetime import date, datetime

from typing import Dict, Any, List

from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy import String, create_engine, ForeignKey, func, event, Text, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, mapped_column, Mapped
from sqlalchemy.dialects import postgresql

engine = create_async_engine('postgresql+asyncpg://admin:admin@postgres:5432/postgres')
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(16), nullable=False)
    api_key: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name
        }


class Tweets(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    attachments: Mapped[List[str]] = mapped_column(postgresql.ARRAY(String), default=[])
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    author: Mapped[List["Users"]] = relationship("Users", backref='tweets')

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tweet_id: Mapped[int] = mapped_column(Integer, ForeignKey('tweets.id'))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    user = relationship("Users", backref="likes")
    tweet = relationship("Tweets", backref="likes")

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}


class Follower(Base):
    __tablename__ = 'followers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    following_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    followers_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    following_f: Mapped[List["Users"]] = relationship("Users", foreign_keys=[following_id], backref="followers")
    followers_f: Mapped[List["Users"]] = relationship("Users", foreign_keys=[followers_id], backref="following")
