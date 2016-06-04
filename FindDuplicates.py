from DbInteractions import *
import re


# TO BE REFACTORED
def equals_doi(p1,p2):
    """ Сравнивает две статьи по ДОИ
        :parameter p1: первая статья(объект класса Publication)
        :parameter p2: вторая статья(объект класса Publication)
        :return True: статьи совпали по ДОИ
        :return False: статьи  не совпали по ДОИ либо ДОИ отсутсвует
    """
    if p1.doi == "None" or p1.doi == "" or p1.doi == "0":
        return False
    if p2.doi == "None" or p2.doi == "" or p2.doi == "0":
        return False
    return p1.doi == p2.doi


# Удаление лишних символов из заголовка и приведение к нижнему регистру
def normalize_title(title):
    return re.sub("[- :.,]", "", title).lower()


def internal_compare_titles(title1, title2):
    """ Сравнивает две статьи по названию. Текст обоих названий приводится к нижнему регистру и из него убираютмся
     все пробелы, точки, тире, двоеточия, запятые.
        :parameter title1: название первой статьи
        :parameter title2: название второй статьи
        :return True: названия совпали
        :return False: названия  не совпали
    """
    return normalize_title(title1) == normalize_title(title2)


def internal_compare_publications(p, comp):
    """ Сравнение двух статей сначала по ДОИ; затем по названию статьи (без преобразования); после по числу авторов,
    длинне названия статьи, упрощенному названию
        :parameter p: первая статья(объект класса Publication)
        :parameter comp: вторая статья(объект класса Publication)
        :return True: статьи совпали
        :return False: статьи  не совпали
   """
    if equals_doi(p, comp):
        return True
    elif p.num_authors == comp.num_authors:
        if internal_compare_titles(p.title, comp.title):
            return True
        else:
            return False

    return False


def find_duplicates_internal(pubs1, pubs2):
    """ Поиск совпадающий статей в 2 списках
        :parameter pubs1: 1 список
        :parameter pubs2: 2 список
        :returns число найденных совпадений
    """
    duplicates_count = 0
    for p in pubs1:
        for comp in pubs2:
            if internal_compare_publications(p, comp):
                duplicates_count += db_insert_duplicate(p, comp)
    return duplicates_count


def find_grouping():
    """ Функция определения совпадающих статей.
    """
    year_inf = 1950
    year_sup = 2016
    duplicates_count = 0
    lst = []
    for year in range(year_inf, year_sup+1):
        ptable = {"scopus":[], "wos":[], "spin":[]}
        for y in [year - 1, year]:
            for source in ptable:
                ptable[source].append(db_select_year(y, source))
        for i1 in [0, 1]:
            for i2 in [0, 1]:
                if i1 == 0 and i2 == 0:
                    continue
                duplicates_count += find_duplicates_internal(ptable["scopus"][i1], ptable["wos"][i2])
                duplicates_count += find_duplicates_internal(ptable["scopus"][i1], ptable["spin"][i2])
                duplicates_count += find_duplicates_internal(ptable["spin"][i1], ptable["wos"][i2])

        print("Checking year", year, " Total duplicates:", str(duplicates_count))