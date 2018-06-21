import re
from logging import getLogger
from urllib import parse


logger = getLogger(__name__)


class MARCXmlParse:
    '''
        given an XML record
        use pymarc to pull out fields:
            author
            notes
            publisher
            pubyear
            subjects
            title
            document symbol
            related documents
    '''
    subject_re = re.compile(r"""
        ^\d{6,7}\s(?:unbis[nt])*\s*(.+)$|
        ^([a-zA-Z ]+)\sunbis[nt]\s\d+$|
        ^unbist\s([a-zA-Z ]+)\s\(DHLAUTH\)\d+$|
        ([a-zA-Z ]+)\sunbist\s\(DHLAUTH\)\d+$""", re.X)

    def __init__(self, record):
        self.record = record

    def subjects(self):
        subjs = {}
        for sub in self.record.subjects():
            logger.debug("Subject: {}".format(sub.value()))
            m = self.subject_re.match(sub.value())
            # kludge!
            # want cleaner way to show subjects
            if m:
                s = m.group(1)
                if not m.group(1):
                    s = m.group(2)
                    if not m.group(2):
                        s = m.group(3)
                        if not m.group(3):
                            s = m.group(4)
                if s:
                    search_string = parse.quote_plus(s)
                    query = "f1=subject&as=1&sf=title&so=a&rm=&m1=p&p1={}&ln=en".format(search_string)
                    subjs[s] = "https://digitallibrary.un.org/search?ln=en&" + query
        logger.debug(subjs)
        return subjs

    def pub_date(self):
        return self.record.pub_date()

    def document_symbol(self):
        return self.record.document_symbol()

    def electronic_location(self):
        return [el for el in self.record.electronic_location()]
