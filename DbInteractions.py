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
        num_pages - количество страниц
        year_publ - год публикации
        id - ид статьи в БД (первичный ключ)
        source - название базы, в которой опубликована статья (SPIN, WoS, SCOPUS)
    """
    db_table = "publication"

    title = TextField()
    authors = TextField()
    num_authors = IntegerField()
    doi = CharField()
    language = CharField()
    keywords = TextField()
    num_pages = CharField()
    year_publ = IntegerField()
    id = PrimaryKeyField()
    source = CharField()

    class Meta:
        database = db_get_instance()


def db_select_year(year, source):
    """ Запрос к БД, возвращающий статьи (в виде списока объектов Publication), которые опубликованы в данный год
        :parameter year: год
        :parameter source: название базы
        :returns pub_list: список статей (в виде списока объектов Publication)
    """
    pub_list = []
    for publication in Publication.select().where((Publication.source == source) &
                                                  (Publication.year_publ == year)):
        pub_list.append(publication)
    return pub_list


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

    def set_id(self,publ):
        if publ.source == "scopus":
            self.id_scopus = publ.id
        elif publ.source == "wos":
            self.id_wos = publ.id
        else:
            self.id_spin = publ.id

    def to_str(self):
        s = "scopus:"
        if self.id_scopus is not None:
            s += str(self.id_scopus)+", "
        s = "wos:"
        if self.id_wos is not None:
            s += str(self.id_wos) + ", "
        s = "spin:"
        if self.id_spin is not None:
            s += str(self.id_spin)

    class Meta:
        database = db_get_instance()


def db_drop_duplicates():
    # drop table
    DuplicateEntry.drop_table(True)


def db_recreate_duplicates():
    # clear duplicates table
    db_drop_duplicates()
    DuplicateEntry.create_table()
    print("Duplicates table created")


def db_search_in_duplicates(id1, id2):
    """ Проверить наличие одной из статей с данными id в базе дубликатов
        :parameter id1: ID первой статьи
        :parameter id2: ID второй статьи
        :returns None: нет совпадения
        :returns DuplicateEntry: запись в БД
    """
    res1 = DuplicateEntry.select().where((DuplicateEntry.id_scopus == id1) |
                                        (DuplicateEntry.id_wos == id1) |
                                        (DuplicateEntry.id_spin == id1))
    res2 = DuplicateEntry.select().where((DuplicateEntry.id_scopus == id2) |
                                         (DuplicateEntry.id_wos == id2) |
                                         (DuplicateEntry.id_spin == id2))
    if res1.count() > 0 and res2.count() > 0:
        return None
    if res1.count() > 0:
        return res1.get()
    elif res2.count() > 0:
        return res2.get()
    return None


def db_update_duplicate(entry, publ1, publ2):
    """ Обновить запись о двойном совпадении, добавив 3 статью
        :parameter entry: Запись в БД
        :parameter publ1: Первая статья
        :parameter publ2: Вторая статья
    """
    entry.set_id(publ1)
    entry.set_id(publ2)
    entry.save()


def db_insert_duplicate(publ1, publ2):
    """ Функция вставки совпадения двух статей в базу
        Если одна из статей уже есть в базе, то создается тройное совпадение (в 3 базах сразу)
        :parameter publ1: Первая статья
        :parameter publ2: Вторая статья
        :returns integer: Количество новых записей о совпадении (0 или 1)
    """
    entry = db_search_in_duplicates(publ1.id, publ2.id)
    if entry is not None:
        db_update_duplicate(entry, publ1, publ2)
        return 0
    # this duplicate is new
    d = DuplicateEntry()
    d.set_id(publ1)
    d.set_id(publ2)
    with db_get_instance().transaction() as txn:
        try:
            d.save()
            res = 1
        except IntegrityError:
            res = 0
        txn.commit()
    return res


def db_count_duplicates():
    """ Подсчет всех совпадений
    """
    return DuplicateEntry.select().count()


def db_count_triples():
    """ Подсчет статей, встречающихся в 3 базах
    """
    return DuplicateEntry.select().where(~(DuplicateEntry.id_scopus >> None) &
                                         ~(DuplicateEntry.id_wos >> None) &
                                         ~(DuplicateEntry.id_spin >> None)).count()


def db_count_excluding(source):
    """ Посчет совпадений, кроме тех, которые включают статьи в данной базе
        Используется для подсчета совпадений в только 2 базах
    """
    if source == "scopus":
        return DuplicateEntry.select().where((DuplicateEntry.id_scopus >> None) &
                                             ~(DuplicateEntry.id_wos >> None) &
                                             ~(DuplicateEntry.id_spin >> None)).count()
    if source == "wos":
        return DuplicateEntry.select().where(~(DuplicateEntry.id_scopus >> None) &
                                             (DuplicateEntry.id_wos >> None) &
                                             ~(DuplicateEntry.id_spin >> None)).count()
    if source == "spin":
        return DuplicateEntry.select().where(~(DuplicateEntry.id_scopus >> None) &
                                             ~(DuplicateEntry.id_wos >> None) &
                                             (DuplicateEntry.id_spin >> None)).count()
    return None
