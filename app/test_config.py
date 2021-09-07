import testing.postgresql
postgresql = testing.postgresql.Postgresql(port=7654)

class Configuration(object):
    SQLALCHEMY_DATABASE_URI = postgresql.url()