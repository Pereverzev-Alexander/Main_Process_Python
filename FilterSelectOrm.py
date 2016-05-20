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
# get all publications from given source: string database ("scopus")
# and year withing year_min: int and year_max: int
def db_select_year_range(year_min,year_max,source):
    pub_list = []
    for publication in Publication.select().where(Publication.source == source):
        year_str = str(publication.year_publ)
        if year_str == "0":
            year = 0
        else:
            try:
                dt = datetime.datetime.fromtimestamp(int(year_str))
                year = int(dt.year)
            except OSError:
                year = 0
        if year >= year_min and year <= year_max:
            #normalize
            if publication.doi == "None" or publication.doi == "0":
                publication.doi = ""
            pub_list.append(publication)
    return pub_list

# #test function
# for p in db_select_year_range(1970,2010,"scopus"):
#     print(p.year_publ+" "+p.title)

# find all articles with same doi
doi_dict = {}
same_doi_publ = []
# insert all articles from scopus, use doi as key
for p in db_select_year_range(0, 3000, "scopus"):
    if p.doi == "":
        continue
    doi_dict[p.doi] = ("scopus",p.id)
# try to insert articles from wos
for p in db_select_year_range(0, 3000, "wos"):
    if p.doi == "":
        continue
    if p.doi in doi_dict:
        same_doi_publ.append(p)
    else:
        doi_dict[p.doi] = ("wos", p.id)
# try to insert articles from spin
for p in db_select_year_range(0, 3000, "spin"):
    if p.doi == "":
        continue
    if p.doi in doi_dict:
        same_doi_publ.append(p)
    else:
        doi_dict[p.doi] = ("spin", p.id)


for o in same_doi_publ:
    print(o.title, o.source, o.doi)
print("Found total  DOI duplicates: "+str(len(same_doi_publ)))