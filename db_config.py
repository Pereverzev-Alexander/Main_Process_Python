from peewee import *


class DbWrapper:
    db = None

    @classmethod
    def get_db_instance(cls):
        if cls.db is None:
            print("Initialize DB connection")
            cls.init_db_instance()
        return cls.db

    @classmethod
    def init_db_instance(cls):
        if cls.db is not None:
            return
        cls.db = PostgresqlDatabase(
            'db',  # Required by Peewee.
            user='postgres',  # Will be passed directly to psycopg2.
            password='admin',
            host='localhost',
        )
        try:
            cls.db.connect()
        except:
            print("Failed to connect to database")
            quit()
        print("Connected to database")


def db_get_instance():
    return DbWrapper.get_db_instance()


def db_init_connect():
    DbWrapper.init_db_instance()