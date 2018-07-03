class Config:
    DEBUG = False
    TESTING = False
    POSTGRES_USER = "smarttagger"
    POSTGRES_PW = "smarttagger"
    POSTGRES_URL = "127.0.0.1:5432"
    POSTGRES_DB = "smarttagger"
    DB_URI = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
        user=POSTGRES_USER,
        pw=POSTGRES_PW,
        url=POSTGRES_URL,
        db=POSTGRES_DB
    )

    TIKA_VERSION = 1.18
    TIKA_SERVER_JAR = "/usr/local/Cellar/tika/1.18/libexec/tika-server-1.17.jar"
    TIKA_SERVER_ENDPOINT = "http://localhost:9998"
    TIKA_CLIENT_ONLY = False
    # TIKA_TRANSLATOR
    # TIKA_SERVER_CLASSPATH
    # TIKA_LOG_PATH
    # TIKA_PATH


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True


class AWSConfig(Config):
    DEBUG = True
