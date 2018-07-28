from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from models.models import Document, Tag, DocumentsTags
from sqlalchemy.sql.expression import func
# from sqlalchemy.sql import text
from db.db import get_session
from collections import defaultdict
from math import floor

session = get_session()

v = CountVectorizer(stop_words='english')


def random_feature_vectors(num_docs):
    '''
    Supervised learning algorithms will require a category label for each document
    in the training set. In this case the category is the document symbol
    '''
    doc_query = session.query(Document).order_by(func.random()).limit(num_docs).all()
    X = v.fit_transform([d.raw_text for d in doc_query])

    #  X_test = v.fit_transform([d.raw_text for d in doc_query[train_size:num_docs]])
    Y = _get_test_train_tags(doc_query)

    return train_test_split(X, Y, 0.25)


def _get_test_train_tags(doc_query, train_size, num_docs):
    symbols_tags = defaultdict(list)
    tags = set()
    for doc in doc_query:
        res = session.query(Tag.tag).join(DocumentsTags). \
            filter(DocumentsTags.c.document_id == doc.id, DocumentsTags.c.tag_id == Tag.id).all()
        for elem in res:
            if len(elem):
                symbols_tags[doc.symbol].append(elem[0])
                tags.update(elem)
            else:
                symbols_tags[doc.symbol].append('')

    mlb = MultiLabelBinarizer(classes=list(tags))
    Y = mlb.fit_transform(symbols_tags.values())
    return Y


def train_test_model(X_train, Y_train, X_test, Y_test):
    mnb = OneVsRestClassifier(MultinomialNB())
    mnb.fit(X_train, Y_train).predict(X_train)
    print('Accuracy testing : {:.3f}'.format(mnb.score(X_test, Y_test)))
    return mnb


def get_top_n_words(corpus, n=None):
    """
    """
    vec = CountVectorizer().fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
    return words_freq[:n]
