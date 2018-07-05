import datetime
from sqlalchemy import Table, Column, Integer, String, Text, DateTime
from sqlalchemy_utils.types.url import URLType
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


DocumentsTags = Table('documents_tags', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('document_id', Integer, ForeignKey('document.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)


class Document(Base):
    __tablename__ = 'document'

    id = Column(Integer, primary_key=True)
    url = Column(URLType, unique=True, nullable=False)
    raw_text = Column(Text, nullable=True)
    symbol = Column(Text, nullable=False)
    tags = relationship("Tag", secondary=DocumentsTags)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.datetime.utcnow)

    def __init__(self, symbol):
        self.symbol = symbol

    def __repr__(self):
        return "<DocumentMetadata: {}".format(self.symbol)

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.undl,
            "symbol": self.symbol
        }


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    tag = Column(String, nullable=False, unique=True)
    uri = Column(URLType, unique=True, nullable=True)
