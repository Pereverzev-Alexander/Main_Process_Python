import psycopg2
import peewee
from peewee import *

db = PostgresqlDatabase(
    'postgres',  # Required by Peewee.
    user='postgres',  # Will be passed directly to psycopg2.
    password='admin',
    host='localhost',
)

try:
    db.connect()
except:
    print("Failed to connect to database")
    quit()
print("Done connection")


# ORM class for Author
# just an example by now
class AuthorModel(Model):
    id = PrimaryKeyField()
    name = CharField()

    class Meta:
        database = db


AuthorModel.create_table()

