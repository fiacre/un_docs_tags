from os.path import join, split
import subprocess
import ssl
from collections import defaultdict
import lxml.etree as ET
from io import BytesIO
from urllib import urlopen, urlparse
# from urllib.parse import unquote, urlsplit
from models import Document, Tag
from logging import getLogger
from proj.config import Config

logger = getLogger(__name__)

DOWNLOAD_DIR = Config.get("DOWNLOAD_DIR", None)


class UNDLConnectionException(Exception):
    pass


class UNDLXmlException(Exception):
    pass


class DocumentManager:
    ns = {'s': 'http://www.loc.gov/MARC21/slim'}

    def __init__(self):
        pass

    def update_document_object(self, **kwargs):
        pass

    def update_tag_objects(self, **kwargs):
        pass

    def get_details_from_undl_url(self, url):
        '''
        fetch a UN Digital Library URL with XML
        given a list of documents described in UNDL xml
        get the raw English text of the document
        the document symbol
        the tags (subjects) of the document
        @url: a fetchable resource that return XML
            in the MARCxml format
        '''
        resp = urlopen(url, context=ssl._create_unverified_context())
        if resp.status != 200:
            logger.debug("query {}, gave status: {}".format(url, resp.status))
            raise UNDLConnectionException
        xml = resp.read()
        if not xml:
            logger.debug("No XML for query: {}".format(url))
            raise UNDLXmlException
        root = ET.fromstring(xml)
        doc_nodes = self._get_document_symbols(root)
        doc_loc = self._get_pdf_links(root)
        symbols = [d.text.strip() for d in doc_nodes]
        links = [l.text.strip('\n') for l in doc_loc]

        symbol_links = dict(zip(symbols, links))

        document_tags = self._get_tags_for_documents(doc_nodes)
        raw_text = []
        for symbol, link in symbol_links.items():
            raw_text.append(self._get_raw_text_from_document(symbol, link))

    def _get_document_symbols(self, root):
        '''
        @root: xml root
        '''
        doc_nodes = root.xpath('.//s:datafield[@tag="191"]/s:subfield[@code="a"]', namespaces=self.ns)
        return doc_nodes

    def _get_pdf_links(self, root):
        '''
        @root: xml root
        '''
        links = root.xpath(
            './/s:datafield[@tag="856"][s:subfield[@code="y"]="English"]/s:subfield[@code="u"]', namespaces=self.ns)
        return links

    def _get_tags_for_documents(self, doc_nodes):
        '''
        @doc: list of xml nodes
        '''
        document_tags = defaultdict(list)
        for elem in doc_nodes:
            tags = elem.xpath('../../s:datafield[@tag="650"]/s:subfield[@code="a"]', namespaces=self.ns)
            document_tags = [t.text.strip() for t in tags]
        return document_tags

    def _get_raw_text_from_document(self, symbol, link):
        cmd = '/Users/andrew/projects/smart_tagger/venv/bin/pdf2txt.py'

        # cur_doc = session.query(Document).query(Document.symbol == symbol)
        if cur_doc:
            logger.error("{} has already been processed".format())
            raise RuntimeError("{} has already been processed".format(symbol))

        resp = urlopen(link, context=ssl._create_unverified_context())
        data = BytesIO(resp.read())
        with open((join(DOWNLOAD_DIR, link), 'wb')) as path:
            path.write(data)
        o = urlparse(link)
        doc_name = split(o.path)[-1]
        completed = subprocess.run([cmd, doc_name], stdout=subprocess.PIPE)

        raw_text = completed.stdout.decode('utf-8')
        return raw_text
