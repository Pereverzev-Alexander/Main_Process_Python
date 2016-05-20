# This file contains function to perform select query using Peewee ORM
# Query gets all articles from given database and year withing given range

import datetime
from peewee import *

# DB connection properties
db = PostgresqlDatabase(
    'db',  # Required by Peewee.
    user='postgres',  # Will be passed directly to psycopg2.
    password='pass',
    host='localhost',
)

# connect to database
try:
    db.connect()
except:
    print("Failed to connect to database")
    quit()
print("Connected to database")


# ORM class for publication
class Publication(Model):
    db_table = "publication"

    title = CharField()
    authors = CharField()
    num_authors = IntegerField()
    doi = CharField()
    language = CharField()
    keywords = CharField()
    range_pages = CharField()
    year_publ = CharField()
    id = PrimaryKeyField()
    source = CharField()

    class Meta:
        database = db


# function to pefrorm select query
def db_select_year_range(year_min,year_max,source):
    pub_list = []
    for publication in Publication.select().where(Publication.source == source):
        year_str = str(publication.year_publ)
        year = int(datetime.datetime.fromtimestamp(int(year_str)).year)
        if year >= year_min and year <= year_max:
            pub_list.append(publication)
    return pub_list

#test function
for p in db_select_year_range(1970,2010,"scopus"):
    print(p.year_publ+" "+p.title)

