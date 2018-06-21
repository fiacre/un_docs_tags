import ssl
from pypdf2xml import pdf2xml
import lxml.etree as ET
from io import BytesIO
from urllib import urlopen
from models import Document, Tag
from logging import getLogger

logger = getLogger(__name__)


class DocumentManager:
    ns = {'s': 'http://www.loc.gov/MARC21/slim'}

    def __init__(self):
        pass

    def get_details_from_undl_xml(self, url):
        '''
        given a list of documents described in UNDL xml
        get the raw English text of the document
        the document symbol
        and the tags
        @url: a fetchable resource that return XML
            in the MARCxml format
        '''
        resp = urlopen(url, context=ssl._create_unverified_context())
        if resp.status != 200:
            logger.debug("query {}, gave status: {}".format(url, resp.status))
            raise
        xml = resp.read()
        if not xml:
            logger.debug("No XML for query: {}".format(url))
            raise
        root = ET.fromstring(xml)
        doc_symbols = self._get_document_symbols(root)
        links = self._get_pdf_links(root)
        a = [d.text.strip() for d in doc_symbols]
        b = [l.text.strip('\n') for l in links]
        data = dict(zip(a, b))

        return data

    def _get_document_symbols(self, root):
        doc_symbols = root.xpath('.//s:datafield[@tag="191"]/s:subfield[@code="a"]', namespaces=self.ns)
        return doc_symbols

    def _get_pdf_links(self, root):
        links = root.xpath(
            './/s:datafield[@tag="856"][s:subfield[@code="y"]="English"]/s:subfield[@code="u"]', namespaces=self.ns)
        return links

    
