# This file contains function to perform select query using Peewee ORM
# Query gets all articles from given database and year withing given range

import datetime
import os
import re
import json
from peewee import *
from db_config import db_get_instance


# ORM class for publication
class Publication(Model):
    """ Класс, представляющий доступ к таблице Публикации в виде объекта
        db_table - название таблицы в БД
        title - название статьи
        authors - инициалы авторов
        num_authors - количество авторов в статье
        doi - ДОИ
        language - язык, на котором написана статья
        keywords - ключевые слова
        range_pages - количество страниц
        year_publ - год публикации
        id - ид статьи в БД (первичный ключ)
        source - название базы, в которой опубликована статья (SPIN, WoS, SCOPUS)
    """
    db_table = "publication"

    title = CharField()
    authors = CharField()
    num_authors = IntegerField()
    doi = CharField()
    language = CharField()
    keywords = CharField()
    range_pages = CharField()
    year_publ = IntegerField()
    id = PrimaryKeyField()
    source = CharField()

    class Meta:
        database = db_get_instance()

    def parse_json_SCOPUS(self, dir_json):
        dirs_json = os.listdir(dir_json)
        count = 0
        for x in dirs_json:
            path = os.path.join(dir_json, x)
            data_file = open(path)
            data = data_file.read()
            js = json.loads(data)
            for jsPaper in js:
                if "pubDate" in jsPaper:
                    # datetime.datetime.fromtimestamp не умеет работать с отрицательными значениями, выдает ошибку erreno 22
                    # решение взяли отсюда http://stackoverflow.com/questions/17231711/how-to-create-datetime-from-a-negative-epoch-in-python
                    if jsPaper["pubDate"] < 0:
                        self.year_publ = (datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=jsPaper["pubDate"]/1000)).year
                    else:
                        self.year_publ = datetime.datetime.fromtimestamp(jsPaper["pubDate"]/1000).year
                else:
                    self.year_publ = 0
                if "language" in jsPaper:
                    self.language = jsPaper["language"]
                else:
                    self.language = ""
                if "pageRange" in jsPaper:
                    range_pages_str = jsPaper["pageRange"]
                    if range_pages_str is not None:
                        range_pages_str = range_pages_str.split("-")
                        if len(range_pages_str) == 2:
                            range_pages_only_int0 = re.sub(r"\D", "", range_pages_str[0])
                            range_pages_only_int1 = re.sub(r"\D", "", range_pages_str[1])
                            if range_pages_only_int0.isdigit() and range_pages_only_int1.isdigit():
                                if 0 < int(range_pages_only_int0) < 2147483647 and 0 < int(
                                        range_pages_only_int1) < 2147483647:
                                    self.range_pages = abs(int(range_pages_only_int1) - int(range_pages_only_int0)) + 1
                                else:
                                    self.range_pages = 1
                            else:
                                self.range_pages = 1
                        else:
                            self.range_pages = 1
                    else:
                        self.range_pages = 1
                else:
                    self.range_pages = 1
                if "doi" in jsPaper:
                    self.doi = jsPaper["doi"]
                else:
                    self.doi = ""
                if "titleEn" in jsPaper:
                    jsTitle = jsPaper["titleEn"]
                    if (jsTitle != "") or (jsTitle != "null"):
                        self.title = jsPaper["titleEn"]
                    elif "titleRu" in jsPaper:
                        self.title = jsPaper["titleRu"]
                else:
                    self.title = ""
                self.authors = []
                if isinstance(jsPaper["authors"]["employee"], list):
                    for jsAuthor in jsPaper["authors"]["employee"]:
                        self.authors.append(jsAuthor["name"])
                if isinstance(jsPaper["authors"]["external"], list):
                    for jsAuthor in jsPaper["authors"]["external"]:
                        self.authors.append(jsAuthor["name"])
                if isinstance(jsPaper["authors"]["unknownInternal"], list):
                    for jsAuthor in jsPaper["authors"]["unknownInternal"]:
                        self.authors.append(jsAuthor["name"])
                if "keywords" in jsPaper:
                    self.keywords = jsPaper["keywords"]
                self.num_authors = len(self.authors)
                self.source = "scopus"
                self.save()
                count += 1
                print(count)


# Test
t = Publication()
Publication.parse_json_SCOPUS(t,r'publications\scopus')
quit()

# unify None and invalid fields format
def normalize_publication(publication):
    """ Приведение полей (doi и range_pages) статьи к общему виду
        :parameter publication: объект класса Publication
        :returns publication: нормализованная объект
    """
    if publication.doi == "None" or publication.doi == "0":
        publication.doi = ""
    if publication.range_pages == "None":
        publication.range_pages = ""
    return publication


# get publication year as integer from datetime in table entry
def get_publication_year(publication):
    """ Получение года публикации статьи из объекта Publication
        :parameter publication: объект класса Publication
        :returns year: год публикации
    """
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
    """ Запрос к БД, возвращающий статьи (в виде списока объектов Publication), которые опубликованы в период между
    годами из определенной базы (SPIN, WoS, SCOPUS)
        :parameter year_min: нижняя граница
        :parameter year_max: верхняя граница
        :parameter source: название базы
        :returns pub_list: список статей (в виде списока объектов Publication)
    """
    pub_list = []
    for publication in Publication.select().where(Publication.source == source and
                                                                          year_min <= Publication.year_publ <= year_max):
        normalize_publication(publication)
        pub_list.append(publication)
    return pub_list


# test function
# for p in db_select_year_range(1970, 1980, "scopus"):
#     print(str(p.year_publ) + " " + p.title)


# function to perform select query
# get all publications without doi and
# publications that do not coincide on doi
def db_select_notDOI_publication():
    """ Запрос к БД, возвращающий статьи (в виде списока объектов Publication), которые не сопадают по ДОИ либо не
    имеют его
        :returns pub_list: список статей (в виде списока объектов Publication)
    """
    pub_list = []
    for publication in Publication.select().where(Publication.doi.not_in(Publication.select(
            Publication.doi).where((Publication.doi != '0') & (Publication.doi != 'None')).group_by(
        Publication.doi).having(fn.Count('*') > 1))):
        # normalize
        normalize_publication(publication)
        pub_list.append(publication)
    return pub_list


# #test function

# #test function
# listPub = db_select_notDOI_publication()
# for p in listPub:
#      print(p.year_publ+" "+p.doi)
# print("Count publications " + str(len(listPub)))


# select all articles from source
def db_select_all(source):
    """ Запрос к БД, возвращающий статьи (в виде списока объектов Publication)из определенной базы (SPIN, WoS, SCOPUS)
        :parameter source: название базы
        :returns pub_list: список статей (в виде списока объектов Publication)
    """
    pub_list = []
    for publication in Publication.select().where(Publication.source == source):
        normalize_publication(publication)
        pub_list.append(publication)
    return pub_list


# # test function
# print(len(db_select_all("scopus"))+len(db_select_all("wos"))+len(db_select_all("spin")))


def db_select_year_source(year_min, year_max, source1, source2):
    """ Запрос к БД, возвращающий статьи (в виде списока объектов Publication), которые опубликованы в период между
    годами из двух баз (SPIN, WoS, SCOPUS)
        :parameter year_min: нижняя граница
        :parameter year_max: верхняя граница
        :parameter source1: название первой базы
        :parameter source2: название второй базы
        :returns pub_list: список статей (в виде списока объектов Publication)
    """
    pub_list = []
    for publication in Publication.select().where((Publication.source << [source1,source2]) &
                                                   Publication.year_publ.between(year_min,year_max)):
        normalize_publication(publication)
        pub_list.append(publication)
    return pub_list


def db_select_year(year_min, year_max, source):
    """ Запрос к БД, возвращающий статьи (в виде списока объектов Publication), которые опубликованы в период между
    годами из определенной базы (SPIN, WoS, SCOPUS)
        :parameter year_min: нижняя граница
        :parameter year_max: верхняя граница
        :parameter source: название базы
        :returns pub_list: список статей (в виде списока объектов Publication)
    """
    pub_list = []
    for publication in Publication.select().where((Publication.source == source) &
                                                   Publication.year_publ.between(year_min,year_max)):
        normalize_publication(publication)
        pub_list.append(publication)
    return pub_list

# for p in db_select_year_source(2000,2000,"scopus","spin"):
#     print(p.source, p.year_publ)


class DuplicateEntry(Model):
    """ Класс, представляющий доступ к таблице Дубликаты в виде объект. В таблице Дубликаты хранятся идентификаторы
    совпадающих статей из таблицы Публикации
        id - первичный ключ
        id_scopus - внешний ключ, указывающий на статьью из базы SCOPUS
        id_wos - внешний ключ, указывающий на статьью из базы WoS
        id_spin - внешний ключ, указывающий на статьью из базы SPIN
    """
    id = PrimaryKeyField(verbose_name="id")
    id_scopus = ForeignKeyField(Publication, related_name="scopus_pubs", unique=True, null=True, verbose_name="id_scopus")
    id_wos = ForeignKeyField(Publication, related_name="wos_pubs", unique=True, null=True, verbose_name="id_wos")
    id_spin = ForeignKeyField(Publication, related_name="spin_pubs", unique=True, null=True, verbose_name="id_spin")

    class Meta:
        database = db_get_instance()

# clear duplicates table
DuplicateEntry.drop_table(True)
DuplicateEntry.create_table()
print("Duplicates table created")


def db_load_duplicates(duplicates):
    """ Загрузка в таблицу Дубликаты идетификаторов совпадающих статей.
        :parameter duplicates: объект класса DuplicateEntry
    """
    print("Inserting "+str(len(duplicates.duplicates))+" entries")
    count_fails = 0
    db = db_get_instance()
    for d in duplicates.duplicates:
        with db.transaction() as txn:
            try:
                DuplicateEntry.create(id_scopus=d.get_scopus_id(), id_wos=d.get_wos_id(), id_spin=d.get_spin_id())
            except:
                count_fails += 1
            txn.commit()

    print("Duplicates in same database: "+str(count_fails))


