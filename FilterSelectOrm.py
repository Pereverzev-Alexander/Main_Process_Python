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


# unify None and invalid fields format
def normalize_publication(publication):
    if publication.doi == "None" or publication.doi == "0":
        publication.doi = ""
    if publication.range_pages == "None":
        publication.range_pages = ""
    return publication


# get publication year as integer from datetime in table entry
def get_publication_year(publication):
    year_str = str(publication.year_publ)
    if year_str == "0":
        year = 0
    else:
        try:
            dt = datetime.datetime.fromtimestamp(int(year_str))
            year = int(dt.year)
        except OSError:
            year = 0
    return year


# function to perform select query
# get all publications from given source: string database ("scopus")
# and year withing year_min: int and year_max: int
def db_select_year_range(year_min, year_max, source):
    pub_list = []
    for publication in Publication.select().where(Publication.source == source):
        year = get_publication_year(publication)
        if year >= year_min and year <= year_max :
            #normalize
            normalize_publication(publication)
            pub_list.append(publication)
    return pub_list

# #test function
# for p in db_select_year_range(1970,2010,"scopus"):
#     print(p.year_publ+" "+p.title)


# select all articles from source
def db_select_all(source):
    pub_list = []
    for publication in Publication.select().where(Publication.source == source):
        normalize_publication(publication)
        pub_list.append(publication)
    return pub_list


# # test function
# print(len(db_select_all("scopus"))+len(db_select_all("wos"))+len(db_select_all("spin")))

