from DbInteractions import *
import re
from transliterate import translit, detect_language
from fuzzywuzzy import fuzz


# class to store found duplicates
class Duplicate:
    """ Класс для хранения всех дубликатов одной статьи

    Поля:
    scopus_p -- дубликат в SCOPUS
    wos_p -- дубликат в WOS
    spin_p -- дубликат в SPIN
    Методы:
    __str__ -- получить  строковое представление
    __repr__ -- получить формальное строковое представление
    insert -- добавить статью в дубликаты
    count_instances -- посчитать, в скольких базах повторяется статья
    get_scopus_id -- получить ID в SCOPUS
    get_wos_id -- получить ID в WOS
    get_spin_id -- получить ID в SPIN

    """
    def __str__(self):
        """ Получить строку, с ID дубликатов в соответствующих базах

        :return: строка с ID дубликатов в соотвтетствующих базах
        """
        res = "duplicate: "
        if self.scopus_p is not None:
            res += " scopus: " + str(self.scopus_p.id)
        if self.wos_p is not None:
            res += " wos: " + str(self.wos_p.id)
        if self.spin_p is not None:
            res += " spin: " + str(self.spin_p.id)
        return res

    def __repr__(self):
        res = "repr: "
        return res

    def insert(self, publication):
        """ Добавление  статьи в дубликаты

        :param publication: добавляемая статься
        :return: нет возвращаемого значения
        """
        if publication.source == "scopus":
            self.scopus_p = publication
        elif publication.source == "wos":
            self.wos_p = publication
        else:
            self.spin_p = publication

    scopus_p = None
    wos_p = None
    spin_p = None

    # number of databases, in which publication is registered
    def count_instances(self):
        """ Функция для подсчёта баз, в которых есть дубликаты статьи

        :return: количество баз, в которых есть дубликаты статьи
        """
        count = 0
        if self.scopus_p is not None:
            count += 1
        if self.wos_p is not None:
            count += 1
        if self.spin_p is not None:
            count += 1
        return count

    # get id of scopus publication,
    # or None, if publication is None
    def get_scopus_id(self):
        """ Получить SCOPUS_ID

        :return: SCOPUS_ID
        """
        if self.scopus_p is not None:
            return self.scopus_p.id
        return None

    def get_wos_id(self):
        """ Получить WOS_ID

        :return: WOS_ID
        """
        if self.wos_p is not None:
            return self.wos_p.id
        return None

    def get_spin_id(self):
        """ Получить SPIN_ID

        :return: SPIN_ID
        """
        if self.spin_p is not None:
            return self.spin_p.id
        return None

    # get publication by source string
    def get_publication(self,source):
        if source == "scopus":
            return self.scopus_p
        if source == "wos":
            return self.wos_p
        if source == "spin":
            return self.spin_p
        return None


# class to store all duplicates
# does fast insertion
class DuplicatesStorage:
    """ Класс для хранения всех дубликатов статей, имеющих дубликаты
    Поля:
    duplicates -- список дубликатов
    """
    duplicates = []
    id_dict = {}

    # insert new publication in duplicates list
    def insert(self, publication, duplicate):
        """ Добаление статьи в спискок дубликатов
            :parameter publication: статья в виде объекта Publication
            :parameter duplicate: список дубликотов
        """
        # check if this publication is already duplicate
        if duplicate.id in self.id_dict:
            # get index of duplicate entry in list
            index = self.id_dict[duplicate.id]
            # add publication to duplicate entry
            self.duplicates[index].insert(publication)
            # add new id key to registered duplicates
            self.id_dict[publication.id] = index
        elif publication.id in self.id_dict:
            # get index of duplicate entry in list
            index = self.id_dict[publication.id]
            # add publication to duplicate entry
            self.duplicates[index].insert(duplicate)
            # add new id key to registered duplicates
            self.id_dict[duplicate.id] = index
        else:
            # create new duplicate
            d = Duplicate()
            d.insert(publication)
            d.insert(duplicate)
            self.duplicates.append(d)
            # save index of entry in duplicates list in dictionary
            self.id_dict[publication.id] = len(self.duplicates)-1

    # return number of publications in all 3 databases
    def get_triples_count(self):
        """ Возвращает количество статьей во всех трех базах (SPIN, SCOPUS, WoS)
            :return count: количество статей
        """
        count = 0
        for d in self.duplicates:
            if d.scopus_p is not None and d.wos_p is not None and d.spin_p is not None:
                count += 1
        return count

    # return number of publication registered in two given databases
    # sources are string names
    def get_count_sources(self, source1, source2):
        """ Возвращает количество зарегистрированных статей в двух выбранных базах данных
            :parameter source1: название первой базы
            :parameter source2: название второй базы
            :return count: количество статей
        """
        count = 0
        for d in self.duplicates:
            if d.get_publication(source1) is not None and d.get_publication(source2) is not None:
                count += 1
        return count


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

        # len1 = len(p.title)
        # len2 = len(comp.title)
        # len_diff = abs(len1 - len2)
        # if len_diff > 5:
        #     return False

        if internal_compare_titles(p.title, comp.title):
            return True
        else:
            # ratio = fuzz.ratio(p.title, comp.title)
            # if ratio > 95:
            #     return True
            return False

    return False


def find_duplicates_internal(pubs1, pubs2, pubs3, duplicates):
    """ Поиск дубликатов статей
        :parameter pubs1: первый список статей для сравнения (SPIN)
        :parameter pubs2: второй список статей для сравнения (WoS)
        :parameter pubs3: третий список статей для сравнения (SCOPUS)
        :return duplicates: список совпавших статьей
   """
    for p in pubs1:
        for comp in pubs2:
            if internal_compare_publications(p, comp):
                duplicates.insert(p, comp)
        for comp in pubs3:
            if internal_compare_publications(p, comp):
                duplicates.insert(p, comp)


def compare_second_name_author(pub1, pub2):
    """ Сравнение двух статей по первой фамилии авторов. Фамилии транслителированны и приведены к нижнему регистру.
        :parameter pub1: первая статья(объект класса Publication)
        :parameter pub2: вторая статья(объект класса Publication)
        :return True: статьи совпали
        :return False: статьи  не совпали
    """
    first_author = pub1.authors[0:pub1.authors.find(' ')]
    second_author = pub2.authors[0:pub2.authors.find(' ')]
    if detect_language(first_author) == 'ru':
        first_author = translit(first_author, reversed=True)
    if detect_language(second_author) == 'ru':
        second_author = translit(second_author, reversed=True)
    if first_author.lower() == second_author.lower():
        return True
    else:
        return False


def find_grouping(duplicates):
    """ Функция определения совпадающих статей.
    """
    year_inf = 1860
    year_sup = 2016
    for year in range(year_inf, year_sup):
        year_min = year - 1
        year_max = year + 1
        pubs_scopus = db_select_year(year_min,year_max,"scopus")
        pubs_wos = db_select_year(year_min, year_max, "wos")
        pubs_spin = db_select_year(year_min, year_max, "spin")
        pubs_scopus_strict = db_select_year(year, year, "scopus")
        pubs_wos_strict = db_select_year(year, year, "wos")
        pubs_spin_strict = db_select_year(year, year, "spin")
        total_len = len(pubs_scopus) + len(pubs_wos) + len(pubs_spin)
        print("Check years",year_min,year_max,"Total articles:",total_len)
        if total_len < 2:
            continue
        find_duplicates_internal(pubs_scopus_strict, pubs_wos, pubs_spin, duplicates)
        find_duplicates_internal(pubs_wos_strict, pubs_scopus, pubs_spin, duplicates)
        find_duplicates_internal(pubs_spin_strict, pubs_wos, pubs_scopus, duplicates)
        print("Total duplicates:", len(duplicates.duplicates))

