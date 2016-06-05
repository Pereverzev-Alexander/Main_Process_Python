# Модуль для заполнения базы данных данными, полученными из JSON - строк
import json
import os
import re
import datetime
from DbInteractions import Publication, db_drop_duplicates


def normalize_page_range_publication(range_pages_str):
    """ Функция определения количесвта страниц, занимемых в журнале
        :parameter range_pages_str: диапазон страниц
        :return - количесвто занимаемых страниц
    """
    if range_pages_str is not None:
        range_pages_str = range_pages_str.split("-")
        range_pages_only_int0 = re.sub(r"\D", "", range_pages_str[0])
        if len(range_pages_str) == 2:
            range_pages_only_int1 = re.sub(r"\D", "", range_pages_str[1])
            if range_pages_only_int0.isdigit() and range_pages_only_int1.isdigit():
                if 0 < int(range_pages_only_int0) < 2147483647 and 0 < int(
                        range_pages_only_int1) < 2147483647:
                    return abs(int(range_pages_only_int1) - int(range_pages_only_int0)) + 1
        else:
            # В статье может быть указан не диапазон, а сразу число страниц
            if range_pages_only_int0.isdigit():
                return int(range_pages_only_int0)

    return 1


def open_json_file(dir_json, curr_json):
    """ Функция открытия json файла в указанной директории
        :parameter dir_json: путь к директории, в которой лежат json файлы
        :parameter curr_json название json файла, который бутет открыт
        :return открытый и распарсенный json файл
    """
    path = os.path.join(dir_json, curr_json)
    data_file = open(path)
    data = data_file.read()
    return json.loads(data)


def check_field_publication(publication):
    """ Функция проверки инициализации полей класса Publication
        :parameter publication: объект класса Publication, представляющий информацию о статье
        :return publication: проинициализированный объект
    """
    if publication.doi is None:
        publication.doi = ""
    if publication.authors is None:
        publication.authors = ""
    if publication.title is None:
        publication.title = ""
    if publication.num_pages is None:
        publication.num_pages = 0
    if publication.num_authors is None:
        publication.num_authors = 0
    if publication.language is None:
        publication.language = ""
    if publication.year_publ is None:
        publication.year_publ = 0
    if publication.keywords is None:
        publication.keywords = ""
    return publication


def load_json_scopus_in_db(dir_json):
    """ Функция загрузки информации о статье в БД из json файлов Scopus'a
        :parameter dir_json: путь к директории, содержащей json файлы
        :return count: колчиство статей, запсианных в БД
    """
    dirs_json = os.listdir(dir_json)
    count = 0
    for x in dirs_json:
        js = open_json_file(dir_json, x)
        for jsPaper in js:
            publication = Publication()
            if "pubDate" in jsPaper:
                # datetime.datetime.fromtimestamp не умеет работать с отрицательными значениями, выдает ошибку erreno 22
                # решение взяли отсюда http://stackoverflow.com/questions/17231711/how-to-create-datetime-from-a-negative-epoch-in-python
                if jsPaper["pubDate"] < 0:
                    publication.year_publ = (datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=jsPaper["pubDate"] / 1000)).year
                else:
                    publication.year_publ = datetime.datetime.fromtimestamp(jsPaper["pubDate"] / 1000).year
            if "language" in jsPaper:
                publication.language = jsPaper["language"]
            if "pageRange" in jsPaper:
                publication.num_pages = normalize_page_range_publication(jsPaper["pageRange"])
            if "doi" in jsPaper:
                publication.doi = jsPaper["doi"]
            if "titleEn" in jsPaper:
                jsTitle = jsPaper["titleEn"]
                if (jsTitle != "") or (jsTitle != "null"):
                    publication.title = jsPaper["titleEn"]
                elif "titleRu" in jsPaper:
                    publication.title = jsPaper["titleRu"]
            publication.authors = []
            if isinstance(jsPaper["authors"]["employee"], list):
                for jsAuthor in jsPaper["authors"]["employee"]:
                    publication.authors.append(jsAuthor["name"])
            if isinstance(jsPaper["authors"]["external"], list):
                for jsAuthor in jsPaper["authors"]["external"]:
                    publication.authors.append(jsAuthor["name"])
            if isinstance(jsPaper["authors"]["unknownInternal"], list):
                for jsAuthor in jsPaper["authors"]["unknownInternal"]:
                    publication.authors.append(jsAuthor["name"])
            if "keywords" in jsPaper:
                publication.keywords = jsPaper["keywords"]
            publication.num_authors = len(publication.authors)
            db_save_publication(publication, "scopus")
            count += 1
            print(count)
    return count


def load_json_spin_in_db(dir_json):
    """ Функция загрузки информации о статье в БД из json файлов Spin'a
        :parameter dir_json: путь к директории, содержащей json файлы
        :return count: колчиство статей, запсианных в БД
    """
    dirs_json = os.listdir(dir_json)
    count = 0
    for x in dirs_json:
        js = open_json_file(dir_json, x)
        for jsPaper in js:
            publication = Publication()
            if "yearpubl" in jsPaper:
                publication.year_publ = jsPaper["yearpubl"]
            elif "source" in jsPaper:
                if isinstance(jsPaper["source"]["issue"], dict):
                    jsYear = jsPaper["source"]["issue"]
                    publication.year_publ = int(jsYear["year"])
            if "language" in jsPaper:
                publication.language = jsPaper["language"]
            if "pages" in jsPaper:
                publication.num_pages = normalize_page_range_publication(jsPaper["pages"])
            if "codes" in jsPaper:
                if isinstance(jsPaper["codes"]["code"], dict):
                    jsDoi = jsPaper["codes"]["code"]
                    if jsDoi["type"] == "DOI":
                        publication.doi = jsDoi["text"]
            if "titles" in jsPaper:
                inst = jsPaper["titles"]["title"]
                if isinstance(inst, dict):
                    publication.title = inst["text"]
                elif isinstance(inst, list):
                    # we prefer english title
                    for title in inst:
                        if title["lang"] == "EN":
                            publication.title = title["text"]
                    # if EN not found, use russian
                    if publication.title is None:
                        publication.title = inst[0]["text"]
                else:
                    print("none")
            publication.authors = []
            if isinstance(jsPaper["authors"]["author"], list):
                for jsAuthor in jsPaper["authors"]["author"]:
                    str_author = jsAuthor["lastname"]
                    if "initials" in jsAuthor:
                        str_author = str_author + " " + jsAuthor["initials"]
                    publication.authors.append(str_author)
            elif isinstance(jsPaper["authors"]["author"], dict):
                jsAuthor = jsPaper["authors"]["author"]
                str_author = jsAuthor["lastname"]
                if "initials" in jsAuthor:
                    str_author = str_author + " " + jsAuthor["initials"]
                publication.authors.append(str_author)
            publication.keywords = []
            if "keywords" in jsPaper:
                if isinstance(jsPaper["keywords"]["keyword"], list):
                    for jsKeywords in jsPaper["keywords"]["keyword"]:
                        if "text" in jsKeywords:
                            keyword = jsKeywords["text"]
                        publication.keywords.append(keyword)
                elif isinstance(jsPaper["keywords"]["keyword"], dict):
                    publication.keywords.append(jsPaper["keywords"]["keyword"]["text"])
            publication.num_authors = len(publication.authors)
            db_save_publication(publication, "spin")
            print(count)
            count += 1
    return count


def load_json_wos_in_db(dir_json):
    """ Функция загрузки информации о статье в БД из json файлов WoS'a
        :parameter dir_json: путь к директории, содержащей json файлы
        :return count: колчиство статей, запсианных в БД
    """
    dirs_json = os.listdir(dir_json)
    count = 0
    for x in dirs_json:
        js = open_json_file(dir_json, x)
        for jsPaper in js:
            publication = Publication()
            if "pub_date" in jsPaper:
                publication.year_publ = int(jsPaper["pub_date"][0:4])
            if "static_data" in jsPaper:
                if isinstance(jsPaper["static_data"]["fullrecord_metadata"], dict):
                    if isinstance(jsPaper["static_data"]["fullrecord_metadata"]["languages"]["language"], dict):
                        publication.language = jsPaper["static_data"]["fullrecord_metadata"]["languages"]["language"][
                                "text"]
            if "page_range" in jsPaper:
                publication.num_pages = normalize_page_range_publication(jsPaper["page_range"])
            if "doi" in jsPaper:
                publication.doi = jsPaper["doi"]
            if "title_en" in jsPaper:
                publication.title = jsPaper["title_en"]
            publication.authors = []
            if isinstance(jsPaper["authors"], list):
                if len(jsPaper["authors"]) >= 1:
                    for jsAuthor in jsPaper["authors"]:
                        if "last_name" in jsAuthor:
                            str_author = jsAuthor["last_name"]
                        if "first_name" in jsAuthor:
                            str_author = str_author + " " + jsAuthor["first_name"]
                        publication.authors.append(str_author)

            publication.keywords = []
            if "keywords" in jsPaper:
                if isinstance(jsPaper["keywords"], list):
                    publication.keywords = jsPaper["keywords"]
            publication.num_authors = len(publication.authors)
            db_save_publication(publication, "wos")
            print(count)
            count += 1
    return count


def db_save_publication(publication, source):
    """ Запись в БД
    """
    publication.source = source
    publication = check_field_publication(publication)
    publication.save()


def db_drop_publications():
    """ Функция пересоздания таблициы в БД, хранящей инфоромацию о статьях
    """
    # clear duplicates table
    db_drop_duplicates()
    Publication.drop_table(True)
    Publication.create_table()
    print("Publications table created")


# main part
db_drop_publications()
# load articles from Spin
count_spin = load_json_spin_in_db(r'publications\spin')
# load articles from Scopus
count_scopus = load_json_scopus_in_db(r'publications\scopus')
# load articles from WoS
count_wos = load_json_wos_in_db(r'publications\wos')
print("Articles uploaded to the database ", str(count_scopus + count_spin + count_wos))
