from urllib.parse import urlparse, parse_qsl, urlencode, ParseResult
from logging import getLogger
from models.models import Document, Tag, DocumentsTags
from sqlalchemy.exc import IntegrityError
from .xml_parse import XmlParse

logger = getLogger(__name__)


class DocumentManager:
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
        cur_count = 0
        o = urlparse(self.url)
        query_dict = dict(parse_qsl(o.query))
        if 'jrec' in query_dict.keys():
            cur_count = items_per_page + 1
        else:
            cur_count += int(query_dict['jrec'])
        if cur_count > limit:
            cur_count = limit
        query_dict.update({'jrec': cur_count})
        query_dict = urlencode(query_dict, doseq=True)
        new_url = ParseResult(
            o.scheme, o.netloc, o.path,
            o.params, query_dict, o.fragment
        ).get_url()
        return new_url

    def insert_documents_and_tags(self):
        '''
        @url: undl url
        pass @url to XmlParse object
        three dictionaries are returned
        from get_details_from_undl_url
        symbols_links, symbols_tags, symbols_text
        add data to ORM Document and Tag objects
        '''
        parser = XmlParse(self.url)
        symbols_links, symbols_tags, symbols_text = parser.get_details_from_undl_url()
        print(symbols_links)
        for symbol, url in symbols_links.items():
            doc = Document(symbol=symbol, url=url, raw_text=symbols_text[symbol])
            for tag in symbols_tags[symbol]:
                t = self._insert_tag(tag)
                if t:
                    self.session.add(t)
                    doc.tags.append(t)
            self.session.add(doc)
            self.session.commit()

    def _insert_document(self, symbol, url, raw_text, *tags):
        query = self.session.query(Document).filter_by(symbol=symbol)
        if query.count() >= 1:
            return None
        try:
            doc = Document(symbol=symbol, url=url, raw_text=raw_text, tags=tags)
            self.session.add(doc)
            self.session.commit()
        except IntegrityError as err:
            logger.error("caught IntegrityError for document {} : {}".format(symbol, err))
            return None
        else:
            return doc

    def _insert_tag(self, tag, uri=None):
        query = self.session.query(Tag).filter_by(tag=tag)
        if query.count() >= 1:
            return None
        t = Tag(tag=tag, uri=uri)
        self.session.add(t)
        try:
            self.session.commit()
        except IntegrityError as err:
            logger.error("Caught IntegrityError for tag: {}, {}".format(tag, err))
            self.session.rollback()
            return None
        else:
            return t

    def get_document_and_tags(self, symbol):
        pass

    def get_symbols(self):
        pass
