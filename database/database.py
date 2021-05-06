import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models


class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=self.engine)
        self.maker = sessionmaker(bind=self.engine)

    def _get_or_create(self, session, model, filter_field, **data):
        instance = session.query(model).filter_by(**{filter_field: data[filter_field]}).first()
        if not instance:
            instance = model(**data)
        return instance

    def add_comments(self, session, data):
        result = []
        for comment in data:
            author = self._get_or_create(
                session,
                models.Author,
                "id",
                name=comment["comment"]["user"]["full_name"],
                url=comment["comment"]["user"]["url"],
                id=comment["comment"]["user"]["id"],
            )
            comment_db = self._get_or_create(
                session, models.Comment, "id", **comment["comment"], author=author,
            )
            result.append(comment_db)
            result.extend(self.add_comments(session, comment["comment"]["children"]))
        return result

    def add_post(self, data):
        session = self.maker()
        post = self._get_or_create(session, models.Post, "id", **data["post_data"])
        author = self._get_or_create(session, models.Author, "id", **data["author_data"])
        tags = map(
            lambda tag_data: self._get_or_create(session, models.Tag, "name", **tag_data),
            data["tags_data"],
        )
        post.author = author
        post.tags.extend(tags)
        post.comments.extend(self.add_comments(session, data["comments_data"]))
        try:
            session.add(post)
            session.commit()
        except sqlalchemy.exc.IntegrityError as error:
            print(error)
            session.rollback()
        finally:
            session.close()
