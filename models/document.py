from sqlalchemy import Table, Column, Integer, String, Text
from sqlalchemy_utils.types.url import URLType
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
# from sqlalchemy_utils.types.scalar_list import ScalarListType
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


documents_tags = Table('documents_tags', Base.metadata,
    Column('document_id', Integer, ForeignKey('document.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    url = Column(URLType, unique=True, nullable=False)
    xml = Column(Text, nullable=False)
    raw_text = Column(Text(nullable=True))
    tags = relationship("Tag", secondary=documents_tags)

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return "<DocumentMetadata: {}".format(self.url)

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.undl,
            "xml": self.xml,
            "json": self.json,
            "created": self.created.strftime("%x %X"),
            "updated": self.updated.strftime("%x %X")
        }


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    tag = Column(String(nullable=False, unique=True))
    uri = Column(URLType, unique=True, nullable=False)

    document_id = Column(Integer, ForeignKey('documents.id'))
    documents = relationship("Document", relationship('Document'))
