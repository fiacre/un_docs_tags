from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from models.models import Document, Tag, DocumentsTags
from sqlalchemy.sql.expression import func
# from sqlalchemy.sql import text
from db.db import get_session, connection
from collections import defaultdict

session = get_session()

v = CountVectorizer(stop_words='english')
conn = connection()


def random_feature_vector(num_docs):
    '''
    Supervised learning algorithms will require a category label for each document
    in the training set. In this case the category is the document symbol
    '''
    train_size = int(num_docs * 0.8)
    doc_query = session.query(Document).order_by(func.random()).limit(num_docs).all()
    X_train = v.fit_transform([d.raw_text for d in doc_query[0:train_size]])
    X_test = v.fit_transform([d.raw_text for d in doc_query[train_size + 1:-1]])

    return X_train, X_test


def get_test_train_tags(doc_query, train_size):
    symbols_tags = defaultdict(list)
    tags = set()
    q = doc_query[0:train_size]
    for doc in q:
        res = session.query(Tag.representation).join(DocumentsTags). \
            filter(DocumentsTags.c.document_id == doc.id, DocumentsTags.c.tag_id == Tag.id).all()
        for elem in res:
            if len(elem):
                symbols_tags[doc.symbol].append(elem[0])
                tags.update(elem)

    test_symbols_tags = defaultdict(list)
    test_tags = set()
    q = doc_query[train_size + 1: -1]
    for doc in q:
        res = session.query(Tag.representation).join(DocumentsTags). \
            filter(DocumentsTags.c.document_id == doc.id, DocumentsTags.c.tag_id == Tag.id).all()
        for elem in res:
            if len(elem):
                test_symbols_tags[doc.symbol].append(elem[0])
                test_tags.update(elem)

    mlb = MultiLabelBinarizer(classes=list(tags))
    Y_train = mlb.fit_transform(symbols_tags.values())

    mlb_test = MultiLabelBinarizer(classes=list(test_tags))
    Y_test = mlb_test.fit_transform(test_symbols_tags.values())

    return Y_test, Y_train


def get_top_n_words(corpus, n=None):
    """
    """
    vec = CountVectorizer().fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
    return words_freq[:n]
