from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models.models import Document, Tag, DocumentsTags
from config import Config

DB_URI = getattr(Config, 'DB_URI', None)
engine = create_engine(DB_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def connection():
    connection = engine.connect()
    return connection


def get_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    DocumentsTags.metadata.create_all(bind=engine, checkfirst=True)
    Document.metadata.create_all(bind=engine, checkfirst=True)
    Tag.metadata.create_all(bind=engine, checkfirst=True)
