# online PDF to XML
import ssl
from pypdf2xml import pdf2xml
import lxml.etree as ET
from io import BytesIO
from urllib import urlopen
from models import Document, Tag
from logging import getLogger

logger = getLogger(__name__)


class PDFManager:
    base_url = 'https://digitallibrary.un.org'
    ns = {'s', 'http://www.loc.gov/MARC21/slim'}

    def __init__(self, search, collection):
        '''
        @search: search URL used by digitallibrary.un.org,
            e.g. p=symbol%3A%27S%2Fres%2F*%27
        @collection: collection in UNDL to be searched
            e.g. Resolutions+and+Decisions
            or Draft+resolutions+and+decisions
        '''

        self.search = search
        self.context = ssl._create_unverified_context()

    def _fetch_undl_xml_root(self, pattern):
        '''
            get MARC XML from digitallibrary.un.org via pattern
            @pattern - search string passed to digitalibrary.un.org
        '''
        url = self.base_url + pattern
        resp = urlopen(url, context=ssl._create_unverified_context())
        if resp.status != 200:
            logger.error("query {}, gave status: {}".format(pattern, resp.status))
            raise
        xml = resp.read()
        if not xml:
            logger.error("No XML for query: {}".format(pattern))
            raise
        root = ET.fromstring(xml)
        return root

    def _fetch_all_undl_pdf_links(self, pattern):
        '''
        '''
        root = self._fetch_undl_xml_root(pattern)
        links = root.findall(
            './/{0}datafield[@tag="856"][{0}subfield="English"]/{0}subfield[@code="u"]'.format(self.ns))
        for url in links:
            url.strip()
            data = self._fetch_pdf(url)
            xml = self._to_xml(data)

    def _fetch_pdf(self, url):
        resp = urlopen(
            url,
            context=self.context
        )
        data = BytesIO(resp.read())
        return data

    def _to_xml(self, data):
        data = self._fetch_pdf()
        xml = pdf2xml(data)
        return xml
