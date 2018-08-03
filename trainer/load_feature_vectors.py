import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
# from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from models.models import Document, Tag, DocumentsTags
from sqlalchemy.sql.expression import func
# from sqlalchemy.sql import text
from db.db import get_session
from collections import defaultdict

session = get_session()


def random_feature_vectors(num_docs):
    '''
    Supervised learning algorithms will require a category label for each document
    in the training set. In this case the category is the document symbol
    '''
    v = CountVectorizer(stop_words='english')
    doc_query = session.query(Document).order_by(func.random()).limit(num_docs).all()
    x = np.array([d.raw_text for d in doc_query])
    X = v.fit_transform(x)

    #  X_test = v.fit_transform([d.raw_text for d in doc_query[train_size:num_docs]])
    Y = _get_test_train_tags(doc_query)

    # returns X_train, X_test, y_train, y_test
    return train_test_split(X, Y, test_size=0.33)


def _get_test_train_tags(doc_query):
    symbols_tags = defaultdict(list)
    tags = set()
    i = 0
    for doc in doc_query:
        i += 1
        res = session.query(Tag.tag).join(DocumentsTags). \
            filter(DocumentsTags.c.document_id == doc.id, DocumentsTags.c.tag_id == Tag.id).all()
        if len(res):
            for elem in res:
                symbols_tags[doc.symbol].append(elem[0])
                tags.update(elem)
        else:
            # there are some documents with no tags
            symbols_tags[doc.symbol].append('NONE')
            tags.update(['NONE'])

    print("{} docs".format(i))
    mlb = MultiLabelBinarizer(classes=list(tags))
    y = np.array(list(symbols_tags.values()))
    Y = mlb.fit_transform(y)
    return Y


def train_test_model(X_train, Y_train, X_test, Y_test):
    # mnb = OneVsRestClassifier(MultinomialNB())
    clf = OneVsRestClassifier(LinearSVC())
    clf.fit(X_train, Y_train).predict(X_test)
    print('Accuracy testing : {:.3f}'.format(clf.score(X_test, Y_test)))
    return clf


def get_top_n_words(corpus, n=None):
    """
    """
    vec = CountVectorizer().fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
    return words_freq[:n]
