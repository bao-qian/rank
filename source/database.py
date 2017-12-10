from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


class Database:
    base = declarative_base()

    @staticmethod
    def engine():
        engine = create_engine("sqlite:///rank.db")
        return engine

    @staticmethod
    def session():
        engine = Database.engine()
        session: Session = sessionmaker(bind=engine)()
        return session


def init_db():
    pass
    # Database.base.metadata.create_all(Database.engine)
    # Model.session.commit()
