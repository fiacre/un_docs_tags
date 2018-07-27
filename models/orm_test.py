import datetime
from sqlalchemy import Table, Column, Integer, String, Text, DateTime
from sqlalchemy_utils.types.url import URLType
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


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

    def __repr__(self):
        return "<Document: {}".format(self.symbol)

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

    def __repr__(self):
        return "<Tag: {}".format(self.tag)

POSTGRES_USER = "test_smarttagger"
POSTGRES_PW = "tst_smarttagger"
POSTGRES_URL = "127.0.0.1:5432"
POSTGRES_DB = "test_smarttagger"
DB_URI = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
    user=POSTGRES_USER,
    pw=POSTGRES_PW,
    url=POSTGRES_URL,
    db=POSTGRES_DB
)
engine = create_engine(DB_URI, convert_unicode=True)

DocumentsTags.metadata.create_all(bind=engine)
Document.metadata.create_all(bind=engine)
Tag.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

doca = Document(symbol="there", url="http://foo.bar", raw_text="Lorem Ipsum")
docb = Document(symbol="here", url="http://foo.bar/sdf", raw_text="Lorem Ipsum")
docc = Document(symbol="rawtorotg", url="http://foo.bar/sdfg", raw_text="Lorem Ipsum")

tag1 = Tag(tag="this here")
tag2 = Tag(tag="That there")

doca.tags.append(tag1, tag2)
docb.tags.append(tag1)


session.add([doca, docb, docc])
session.commit()
