# Модуль содержащий функции для поиска статей, имеющих определённые идентичные параметры
from DbInteractions import db_select_year_range


# find articles with the same count author
def find_same_num_authors(year_min, year_max, source1, source2):
    """ Фунцкция для поиска статей с одинаковым количеством авторов в двух базах в указанном временном прмежутке

    :param year_min: нижняя граница промежутка
    :param year_max: верхняя граница промежутка
    :param source1: первая база для поиска
    :param source2: вторая база для поиска
    :return:список идентичных статей
    """
    lst = []
    lst_1 = db_select_year_range(year_min, year_max, source1)
    lst_2 = db_select_year_range(year_min, year_max, source2)
    for p1 in lst_1:
        for p2 in lst_2:
            if p1.num_authors == p2.num_authors:
                lst.append((p1,p2))
    return lst


# returns all articles published within given range
# from given sources with same pages range
def find_same_pages(year_min, year_max, source1, source2):
    """ Функция поиска идентичных статей в двух базах в указанном временном прмежутке

    :param year_min: нижняя граница промежутка
    :param year_max: верхняя граница промежутка
    :param source1: первая база для поиска
    :param source2: вторая база для поиска
    :return:список идентичных статей
    """
    lst = []
    lst_1 = db_select_year_range(year_min, year_max, source1)
    lst_2 = db_select_year_range(year_min, year_max, source2)
    for p1 in lst_1:
        for p2 in lst_2:
            if p1.range_pages == p2.range_pages:
                lst.append((p1,p2))
    return lst

# Тестирование
list_pub = find_same_num_authors(2001, 2001, "spin", "wos")
print("Found with same count authors: "+str(len(list_pub)))

list_pub = find_same_pages(2000, 2000, "scopus", "wos")
print("Found with same pages range: "+str(len(list_pub)))
