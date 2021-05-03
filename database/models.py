from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Table


Base = declarative_base()

tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
)


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    title = Column(String(250), nullable=False, unique=False)
    url = Column(String, unique=True, nullable=False)
    author_id = Column(Integer, ForeignKey("author.id"), nullable=False)
    author = relationship("Author", backref="posts")


class Author(Base):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String(350), nullable=False, unique=False)


class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String(350), nullable=False, unique=False)
    posts = relationship(Post, secondary=tag_post, backref="tags")
