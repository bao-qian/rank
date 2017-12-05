from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


class Database:
    base = declarative_base()
    engine = create_engine("sqlite:///rank.db")
    session: Session = sessionmaker(bind=engine)()


def init_db():
    Database.base.metadata.create_all(Database.engine)
    # Model.session.commit()
