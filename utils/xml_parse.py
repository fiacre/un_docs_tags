from os.path import join, split
from os import remove
import subprocess
import ssl
from collections import defaultdict
import lxml.etree as ET
from urllib.request import urlopen
from urllib.parse import urlparse, unquote
from config import Config
from models.models import Document
from utils.app_logger import logger
from db.db import get_session

session = get_session()


DOWNLOAD_DIR = getattr(Config, "DOWNLOAD_DIR", None)


class UNDLConnectionException(Exception):
    pass


class UNDLXmlException(Exception):
    pass


class XmlParse:
    ns = {'s': 'http://www.loc.gov/MARC21/slim'}

    def __init__(self, url):
        '''
        @url: a resource that return XML
            in the MARCxml format
        '''
        self.url = url

    def get_details_from_undl_url(self):
        '''
        fetch a UN Digital Library URL with XML
        given a list of documents described in UNDL xml
        get the raw English text of the document
        the document symbol
        the tags (subjects) of the document

        '''
        resp = urlopen(self.url, context=ssl._create_unverified_context())
        if resp.status != 200:
            logger.debug("query {}, gave status: {}".format(self.url, resp.status))
            raise UNDLConnectionException
        xml = resp.read()
        if not xml:
            logger.debug("No XML for query: {}".format(self.url))
            raise UNDLXmlException
        root = ET.fromstring(xml)
        doc_nodes = self._get_document_symbols(root)
        doc_loc = self._get_pdf_links(root)
        if not doc_nodes or not doc_loc:
            return None
        symbols = [d.text.strip() for d in doc_nodes]
        links = [l.text.strip('\n') for l in doc_loc]

        symbols_links = dict(zip(symbols, links))
        symbols_tags = self._get_tags_for_documents(doc_nodes)
        symbols_text = defaultdict(list)
        for symbol, link in symbols_links.items():
            query = session.query(Document).filter_by(symbol=symbol)
            if query.count() > 0:
                continue
            symbols_text[symbol] = self._get_raw_text_from_document(link)

        return symbols_links, symbols_tags, symbols_text

    def _get_document_symbols(self, root):
        '''
        @root: xml root
        return the element tree nodes
        collection > record > datafield
        '''
        doc_nodes = None
        doc_nodes = root.xpath('.//s:datafield[@tag="191"]/s:subfield[@code="a"]', namespaces=self.ns)
        return doc_nodes

    def _get_pdf_links(self, root):
        '''
        @root: xml root
        '''
        links = None
        links = root.xpath(
            './/s:datafield[@tag="856"][s:subfield[@code="y"]="English"]/s:subfield[@code="u"]', namespaces=self.ns)
        return links

    def _get_tags_for_documents(self, doc_nodes):
        '''
        @doc_nodes: list of xml nodes
        '''
        document_tags = defaultdict(list)
        for elem in doc_nodes:
            tags = elem.xpath('../../s:datafield[@tag="650"]/s:subfield[@code="a"]', namespaces=self.ns)
            document_tags[elem.text.strip()] = [t.text.strip() for t in tags]
        if not document_tags or document_tags == []:
            raise UNDLXmlException("Could not get tags for current document")
        return document_tags

    def _get_raw_text_from_document(self, link):
        '''
        Want to use tika or some other technology
        that does not force a download -- but this
        will have to do for now.
        '''
        cmd = '/Users/andrew/projects/smart_tagger/venv/bin/pdf2txt.py'

        resp = urlopen(link, context=ssl._create_unverified_context())
        data = resp.read()
        o = urlparse(link)
        doc_name = split(o.path)[-1]
        doc_name = unquote(doc_name)
        try:
            with open(join(DOWNLOAD_DIR, doc_name), 'wb') as path:
                path.write(data)
        except OSError as err:
            logger.error("Could not get text from document: {} {} ".format(doc_name, err))
            return None

        try:
            completed = subprocess.run([cmd, join(DOWNLOAD_DIR, doc_name)], stdout=subprocess.PIPE)
        except OSError as err:
            logger.error('could not scrape text from {}, {}'.format(doc_name, err))
            return None

        raw_text = completed.stdout.decode('utf-8')
        # clean up
        remove(join(DOWNLOAD_DIR, doc_name))
        return raw_text
