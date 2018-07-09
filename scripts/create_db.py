from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists
from config import Config
from models.models import DocumentsTags, Document, Tag

DB_URI = getattr(Config, 'DB_URI', None)

engine = create_engine(DB_URI, convert_unicode=True)

if not database_exists(DB_URI):
    DocumentsTags.metadata.create_all(bind=engine)
    Document.metadata.create_all(bind=engine)
    Tag.metadata.create_all(bind=engine)
    print("Created new database '{}'".format(DB_URI))
else:
    print("Database '{}'' already exists".format(DB_URI))
