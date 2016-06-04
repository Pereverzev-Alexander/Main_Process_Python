# Модуль для подлючения к БД Postgres
from peewee import *


class DbWrapper:
    """Класс, содержащий объект БД и управляющий доступом

        Поля:
        db - объект БД
        """
    db = None


    @classmethod
    def get_db_instance(cls):
        """Получение экземпляра БД
            Если не существует, будет создан и будет выполнено подключение
            """
        if cls.db is None:
            print("Initialize DB connection")
            cls.init_db_instance()
        return cls.db


    @classmethod
    def init_db_instance(cls):
        """Внутренний метод инициализации
            """
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
    """Функия для получения экземпляра объекта БД
    """
    return DbWrapper.get_db_instance()


