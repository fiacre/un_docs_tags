from urllib.parse import urlparse, parse_qsl, urlencode, ParseResult
from logging import getLogger
from models.models import Document, Tag
from db.db import connection
from .xml_parse import XmlParse

logger = getLogger(__name__)

connection = connection()


class DocumentManager:
    '''
    @url: undl url of XML list of document (resolution) data
    @session: database session
    Uses: XmlParse
    methods:
        paginate_undl_results
        insert_documents_and_tags
        get_document_and_tags
        get_symbols

    '''
    def __init__(self, url, session):
        self.url = url
        self.session = session

    def paginate_undl_results(self, items_per_page=25, limit=100):
        '''
        set a search term for digitallibrary
        and use the api (such as it is)
        to get total results back
        and to paginate through those
        results

        if @limit is set, stop after @limit
        '''
        count = 1
        if count == 1:
            yield self.url
        while count + items_per_page < limit:
            o = urlparse(self.url)
            query_dict = dict(parse_qsl(o.query))
            if 'jrec' in query_dict.keys():
                count = int(query_dict['jrec']) + items_per_page + 1
            else:
                count = items_per_page + 1
            query_dict.update({'jrec': count})
            query_dict = urlencode(query_dict, doseq=True)
            new_url = ParseResult(
                o.scheme, o.netloc, o.path,
                o.params, query_dict, o.fragment
            ).geturl()
            yield new_url
            count += items_per_page
            self.url = new_url
            logger.debug(self.url)

    def insert_documents_and_tags(self):
        '''
        pass self.url to XmlParse object
        three dictionaries are returned
        from get_details_from_undl_url method:
        symbols_links, symbols_tags, symbols_text
        add data to ORM Document and Tag objects
        '''
        for u in self.paginate_undl_results():
            self.url = u
            parser = XmlParse(self.url)
            symbols_links, symbols_tags, symbols_text = parser.get_details_from_undl_url()
            logger.debug(symbols_links)
            print("symbols_tags: ", symbols_tags)
            for symbol, document_url in symbols_links.items():
                logger.debug(symbol)
                print(symbol)
                query = self.session.query(Document).filter_by(symbol=symbol)
                if query.count() > 0:
                    # seen this document before
                    continue
                # create new Document object
                doc = Document(symbol=symbol, url=document_url, raw_text=symbols_text[symbol])
                self.session.add(doc)
                self.session.commit()
                for new_tag in symbols_tags[symbol]:
                    query = self.session.query(Tag).filter_by(tag=new_tag)
                    if query.count() > 0:
                        # tag is already in DB
                        # update doc
                        print("Existing Tag: ", query.scalar())
                        doc.tags.append(query.scalar())
                        self.session.commit()
                    else:
                        # tag is new
                        # insert tag and update doc
                        tag = Tag(tag=new_tag)
                        self.session.add(tag)
                        doc.tags.append(tag)
                        self.session.commit()

    def get_document_and_tags(self, symbol):
        '''
        @symbol: document symbol (unique constraint)
        return documet data and tags associated to
        that document
        '''
        pass

    def get_symbols(self):
        '''
        get a list of document symbols
        '''
        pass

    # def _insert_document(self, symbol, url, raw_text, *tags):
    #     query = self.session.query(Document).filter_by(symbol=symbol)
    #     if query.count() >= 1:
    #         return None
    #     try:
    #         doc = Document(symbol=symbol, url=url, raw_text=raw_text, tags=tags)
    #         self.session.add(doc)
    #         self.session.commit()
    #     except IntegrityError as err:
    #         logger.error("caught IntegrityError for document {} : {}".format(symbol, err))
    #         return None
    #     else:
    #         return doc

    # def _insert_or_update_tag(self, tag, doc, uri=None):
    #     query = self.session.query(Tag).filter_by(tag=tag)
    #     if query.count() >= 1:
    #         stmnt = update(Document.__table__).where(Document.symbol == doc.symbol).values(tags=tag)
    #         self.session.execute(stmnt)
    #         return None
    #     t = Tag(tag=tag, uri=uri)
    #     self.session.add(t)
    #     try:
    #         self.session.commit()
    #     except IntegrityError as err:
    #         logger.error("Caught IntegrityError for tag: {}, {}".format(tag, err))
    #         self.session.rollback()
    #         return None
    #     else:
    #         return t
