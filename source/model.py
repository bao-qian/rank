from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


class Model:
    base = declarative_base()
    engine = create_engine("sqlite:///rank.db")
    session: Session = sessionmaker(bind=engine)()


def init_db():
    Model.base.metadata.create_all(Model.engine)
    # Model.session.commit()
