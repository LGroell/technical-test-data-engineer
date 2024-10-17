from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


listen_history_tracks = Table(
    "listen_history_tracks",
    Base.metadata,
    Column("listen_history_id", Integer, ForeignKey("listen_history.id")),
    Column("track_id", Integer, ForeignKey("tracks.id")),
)


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    artist = Column(String)
    songwriters = Column(String)
    duration = Column(String)
    genres = Column(String)
    album = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    listen_histories = relationship(
        "ListenHistory",
        secondary=listen_history_tracks,
        back_populates="tracks",
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    gender = Column(String)
    favorite_genres = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    listen_histories = relationship("ListenHistory", back_populates="user")


class ListenHistory(Base):
    __tablename__ = "listen_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relation avec User
    user = relationship("User", back_populates="listen_histories")

    # Relation many-to-many avec Track
    tracks = relationship(
        "Track",
        secondary=listen_history_tracks,
        back_populates="listen_histories",
    )
