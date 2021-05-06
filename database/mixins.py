from sqlalchemy import Column, String


class UrlMixin:
    url = Column(String, unique=True, nullable=False)
