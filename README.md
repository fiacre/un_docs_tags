## Overview ##

    Adoption of Machine Learning to the Problem of Tagging UN Documents


## Background ##

    Hand tagging of UN Council reports has been the status quo and is error prone as well as time consuming.  Surely there is a better way!



## Motivation ##

    Less work
    Less error prone
    It's Cool!


## Approach ##

Technical Problems
    Multi-label Classification against a Large Label Set -- Scikit learn was built for this type of problem.  Our concern is getting enough data, finding a good classifier and maintinaing that classifier.



Training a Text Classifier (TC)
    Choice of Training Data
        Choose several hundred Security Council Resolution, several hundred General Assembly Resolutions, various Economic and Social Council Resolutions to get a decent set of documents and subject tags
    Persistance of Trained TC:
        Postgres is perfect for this.  We'll use SQLAlchemy as an ORM.

Testing the TC:
    Choice of testing data will be a a slice from a larger set of random documents.  e.g. choose 1000 documents at random, use 800 for training and 200 for testing.

Evaluation of TC
    Precision and Recall are managed for us by scikit-learn.

User Interface:
    Flask application that uses the trained classifier to suggest subject tags given a document.


