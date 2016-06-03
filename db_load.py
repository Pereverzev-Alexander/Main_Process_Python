# Модуль для заполнения базы данных данными, полученными из JSON - строк
import json
import os
import psycopg2
import re
import time
import pprint
import datetime


class Author:
    """Класс, содержащий информацию об авторе

    Поля:
    lastname -- фамилия
    initials -- инициалы
    affiliations -- принадлежность к организации
    Методы:
    __repr__ -- возвращает формальное строковое представление объекта
    """
    lastname = ""
    initials = ""
    affiliations = ""

    def __repr__(self):
        """Возвращает строку, содержащюю в себе всю информацию об авторе"""
        return str(self.lastname) + " " + str(self.initials) + " " + str(self.affiliations)


class Paper:
    """ Класс, соответствующей отдельно взятой статье

    Поля:
    language -- язык статьи
    year_publ -- год публикации. Ноль по - умолчанию
    range_pages -- количество страниц. Ноль по - умолчанию
    title -- название
    keywords -- список ключевых слов
    doi -- ДОИ. Ноль по - умолчанию
    num_authors -- количество авторов
    authors -- список авторов. Ноль по - умолчанию
    Методы:
    __repr__ -- возвращает формальное строковое представление объекта
    """

    language = ""
    year_publ = 0
    range_pages = 0
    title = ""
    keywords = []
    doi = 0
    num_authors = 0
    authors = []

    def __repr__(self):
        """ Возвращает в виде строки ключевые слова, год публикации, ДОИ, авторов,название, язык, и кол - во авторов"""
        return str(self.keywords) + " " + str(self.year_publ) + " " + str(self.doi) + " " + str(
            self.authors) + " " + str(self.title) + " " + str(self.language) + " " + str(self.num_authors)


def IsInt(s):
    """ Проверка на то, является ли строка целым числом

    :param s: исследуемая строка
    :return: возможно ли преобразовать строку s в целое число
    """
    try:
        int(s)
        return True
    except ValueError:
        return False


# connect to db
def connect2db(host_name, db_name, user_name, password):
    """ Функция для подключения к базе данных

    :param host_name:навзание сервера
    :param db_name:название БД
    :param user_name:имя пользователя
    :param password:пароль
    :return: объект подключения
    """
    conn_string = "host='" + host_name + "' dbname='" + db_name + "' user='" + user_name + "' password='" + password + "'"
    conn = psycopg2.connect(conn_string)
    return conn


# insert data to db
def insert(table, columns, values, conn):
    """Функция для вставки в базу данных

    :param table:название таблицы
    :param columns:название столбца
    :param values:значение
    :param conn:объект подключения
    :return:не возвращает значения
    """
    cursor = conn.cursor()
    statement = '''INSERT INTO ''' + table + ''' (''' + columns + ''') VALUES (''' + values + ''')'''
    cursor.execute(statement)
    conn.commit()
    return


# Подключение к БД
host_name = "localhost"
db_name = "db"
user_name = "postgres"
password = "admin"
table = "publication"
columns = "title, authors, num_authors, range_pages, doi, year_publ, language, keywords, source"
pub_count = 1
conn = connect2db(host_name, db_name, user_name, password)

# перебор файлов в директории, path - ссылка на каждый файл
dir_spin = r'publications\spin'
dir_scopus = r'publications\scopus'
dir_wos = r'publications\wos'
dirs_spin = os.listdir(dir_spin)
dirs_scopus = os.listdir(dir_scopus)
dirs_wos = os.listdir(dir_wos)
data_json = []



for x in dirs_spin:
    path = os.path.join(dir_spin, x)
    data_file = open(path)
    data = data_file.read()
    js = json.loads(data)

    papers = []
    counter = 0
    for jsPaper in js:
        counter += 1
        paper = Paper()
        if "yearpubl" in jsPaper:
            paper.year_publ = jsPaper["yearpubl"]
        elif "source" in jsPaper:
            if isinstance(jsPaper["source"]["issue"], dict):
                jsYear = jsPaper["source"]["issue"]
                paper.year_publ = int(jsYear["year"])
        if "language" in jsPaper:
            paper.language = jsPaper["language"]
        if "pages" in jsPaper:
            range_pages_str = ""
            range_pages_str = jsPaper["pages"]
            if len(range_pages_str.split("-")) == 2:
                range_pages_only_int0 = re.sub(r"\D", "", range_pages_str.split("-")[0]);
                range_pages_only_int1 = re.sub(r"\D", "", range_pages_str.split("-")[1]);
                # if IsInt(range_pages_str.split("-")[0]) and IsInt(range_pages_str.split("-")[1]):
                paper.range_pages = int(range_pages_only_int1) - int(range_pages_only_int0) + 1
            elif len(range_pages_str.split("-")) == 1:
                paper.range_pages == 1;
        if "codes" in jsPaper:
            if isinstance(jsPaper["codes"]["code"], dict):
                jsDoi = jsPaper["codes"]["code"]
                if jsDoi["type"] == "DOI":
                    paper.doi = jsDoi["text"]
        if "titles" in jsPaper:
            if isinstance(jsPaper["titles"]["title"], dict):
                if isinstance(jsPaper["titles"]["title"]["text"], str):
                    paper.title = jsPaper["titles"]["title"]["text"]
        paper.authors = []
        if isinstance(jsPaper["authors"]["author"], list):
            for jsAuthor in jsPaper["authors"]["author"]:
                author = Author()
                author.lastname = jsAuthor["lastname"]
                if "initials" in jsAuthor:
                    author.initials = jsAuthor["initials"]
                if "affiliations" in jsAuthor:
                    if isinstance(jsAuthor["affiliations"]["affiliation"], dict):
                        if "orgname" in jsAuthor["affiliations"]["affiliation"]:
                            author.affiliations = jsAuthor["affiliations"]["affiliation"]["orgname"]
                paper.authors.append(author)
        elif isinstance(jsPaper["authors"]["author"], dict):
            jsAuthor = jsPaper["authors"]["author"]
            author = Author()
            author.lastname = jsAuthor["lastname"]
            if "initials" in jsAuthor:
                author.initials = jsAuthor["initials"]
            if "affiliations" in jsAuthor:
                if isinstance(jsAuthor["affiliations"]["affiliation"], dict):
                    if "orgname" in jsAuthor["affiliations"]["affiliation"]:
                        author.affiliations = jsAuthor["affiliations"]["affiliation"]["orgname"]
            paper.authors.append(author)
        paper.keywords = []
        if "keywords" in jsPaper:
            if isinstance(jsPaper["keywords"]["keyword"], list):
                for jsKeywords in jsPaper["keywords"]["keyword"]:
                    if "text" in jsKeywords:
                        keyword = jsKeywords["text"]
                    paper.keywords.append(keyword)
            elif isinstance(jsPaper["keywords"]["keyword"], dict):
                jsKeywords = jsPaper["keywords"]["keyword"]
                keyword = jsKeywords["text"]
                paper.keywords.append(keyword)
        paper.num_authors = len(paper.authors)
        papers.append(paper)
        paper.title = re.sub('(\")', '', paper.title)
        paper.title = re.sub('(\')', "", paper.title)
        paper.authors = re.sub('(\")', '', str(paper.authors))
        paper.authors = re.sub('(\')', "", str(paper.authors))
        paper.keywords = re.sub('(\")', '', str(paper.keywords))
        paper.keywords = re.sub('(\')', "", str(paper.keywords))
        values = "'" + str(paper.title) + "', '" + str(paper.authors) + "', " + str(
            paper.num_authors) + ", '" + str(paper.range_pages) + "', '" + str(paper.doi) + "', '" + str(
            paper.year_publ) + "', '" + str(paper.language) + "','" + str(paper.keywords) + "', 'spin'"
        insert(table, columns, values, conn)
        print(pub_count)
        pub_count += 1


for x in dirs_scopus:
    path = os.path.join(dir_scopus, x)
    data_file = open(path)
    data = data_file.read()
    js = json.loads(data)
    papers = []
    for jsPaper in js:
        paper = Paper()
        if "pubDate" in jsPaper:
            paper.year_publ = jsPaper["pubDate"]
            if paper.year_publ >= 0:
                normal_date = datetime.datetime.fromtimestamp(paper.year_publ/1000)
                paper.year_publ = normal_date.year
            if paper.year_publ < 0:
                normal_date = datetime.datetime.fromtimestamp(-paper.year_publ / 1000)
                paper.year_publ = 1970 - (normal_date.year - 1970)
        if "language" in jsPaper:
            paper.language = jsPaper["language"]
        if "pageRange" in jsPaper:
            range_pages_str = ""
            range_pages_str = jsPaper["pageRange"]
            if range_pages_str is not None:
                    if len(range_pages_str.split("-")) == 2:
                        range_pages_only_int0 = re.sub(r"\D", "", range_pages_str.split("-")[0]);
                        range_pages_only_int1 = re.sub(r"\D", "", range_pages_str.split("-")[1]);
                        # if IsInt(range_pages_str.split("-")[0]) and IsInt(range_pages_str.split("-")[1]):
                        if IsInt(range_pages_only_int0) and IsInt(range_pages_only_int1):
                            if 0 < int(range_pages_only_int0) < 4294967295 and 0 < int(range_pages_only_int1) < 4294967295:
                                paper.range_pages = int(range_pages_only_int1) - int(range_pages_only_int0) + 1
                            else:
                                paper.range_pages = int(1)
                    elif len(range_pages_str.split("-")) == 1:
                        paper.range_pages == 1;
        if "doi" in jsPaper:
            paper.doi = jsPaper["doi"]
        if "titleEn" in jsPaper:
            jsTitle = jsPaper["titleEn"]
            if (jsTitle != "") or (jsTitle != "null"):
                paper.title = jsPaper["titleEn"]
            elif "titleRu" in jsPaper:
                paper.title = jsPaper["titleRu"]
        paper.authors = []
        # maybe have more authers such as student, unkonownInternal
        if isinstance(jsPaper["authors"]["employee"], list):
            for jsAuthor in jsPaper["authors"]["employee"]:
                author = Author()
                author.lastname = jsAuthor["name"].split()[0]
                author.initials = jsAuthor["name"].split()[1]
                if "affiliations" in jsAuthor:
                    if isinstance(jsAuthor["affiliations"], list):
                        if len(jsAuthor["affiliations"]) >= 1:
                            author.affiliations = jsAuthor["affiliations"][0]
                paper.authors.append(author)
        if isinstance(jsPaper["authors"]["external"], list):
            for jsAuthor in jsPaper["authors"]["external"]:
                author = Author()
                author.lastname = jsAuthor["name"].split()[0]
                if len(jsAuthor["name"].split()) > 1:
                    author.initials = jsAuthor["name"].split()[1]
                else:
                    author.initials = "_"
                if "affiliations" in jsAuthor:
                    if isinstance(jsAuthor["affiliations"], list):
                        if len(jsAuthor["affiliations"]) >= 1:
                            author.affiliations = jsAuthor["affiliations"][0]
                paper.authors.append(author)
        if isinstance(jsPaper["authors"]["unknownInternal"], list):
            for jsAuthor in jsPaper["authors"]["unknownInternal"]:
                author = Author()
                author.lastname = jsAuthor["name"].split()[0]
                if len(jsAuthor["name"].split()) > 1:
                    author.initials = jsAuthor["name"].split()[1]
                else:
                    author.initials = "_"
                if "affiliations" in jsAuthor:
                    if isinstance(jsAuthor["affiliations"], list):
                        if len(jsAuthor["affiliations"]) >= 1:
                            author.affiliations = jsAuthor["affiliations"][0]
                paper.authors.append(author)
        paper.keywords = []
        if "keywords" in jsPaper:
            keyword = jsPaper["keywords"]
            paper.keywords.append(keyword)
        paper.num_authors = len(paper.authors)
        papers.append(paper)
        paper.title = re.sub('(\")', '', paper.title)
        paper.title = re.sub('(\')', "", paper.title)
        paper.authors = re.sub('(\")', '', str(paper.authors))
        paper.authors = re.sub('(\')', "", str(paper.authors))
        paper.keywords = re.sub('(\")', '', str(paper.keywords))
        paper.keywords = re.sub('(\')', "", str(paper.keywords))
        values = "'" + str(paper.title) + "', '" + str(paper.authors) + "', " + str(
            paper.num_authors) + ", '" + str(paper.range_pages) + "', '" + str(paper.doi) + "', '" + str(
            paper.year_publ) + "', '" + str(paper.language) + "','" + str(paper.keywords) + "', 'scopus'"
        insert(table, columns, values, conn)
        print(pub_count)
        pub_count += 1

for x in dirs_wos:
    path = os.path.join(dir_wos, x)
    data_file = open(path)
    data = data_file.read()
    js = json.loads(data)
    papers = []
    for jsPaper in js:
        paper = Paper()
        if "pub_date" in jsPaper:
            paper.year_publ = int(jsPaper["pub_date"][0:4])
        if "static_data" in jsPaper:
            if isinstance(jsPaper["static_data"]["fullrecord_metadata"], dict):
                if isinstance(jsPaper["static_data"]["fullrecord_metadata"]["languages"]["language"], dict):
                    if isinstance(jsPaper["static_data"]["fullrecord_metadata"]["languages"]["language"], dict):
                        paper.language = jsPaper["static_data"]["fullrecord_metadata"]["languages"]["language"]["text"]
        if "page_range" in jsPaper:
            range_pages_str = ""
            range_pages_str = jsPaper["page_range"]
            if range_pages_str is not None:
                    if len(range_pages_str.split("-")) == 2:
                        range_pages_only_int0 = re.sub(r"\D", "", range_pages_str.split("-")[0]);
                        range_pages_only_int1 = re.sub(r"\D", "", range_pages_str.split("-")[1]);
                        # if IsInt(range_pages_str.split("-")[0]) and IsInt(range_pages_str.split("-")[1]):
                        if IsInt(range_pages_only_int0) and IsInt(range_pages_only_int1):
                            paper.range_pages = int(range_pages_only_int1) - int(range_pages_only_int0) + 1
                    elif len(range_pages_str.split("-")) == 1:
                        paper.range_pages == 1;
        if "doi" in jsPaper:
            paper.doi = jsPaper["doi"]
        if "title_en" in jsPaper:
            paper.title = jsPaper["title_en"]
        paper.authors = []
        if isinstance(jsPaper["authors"], list):
            if len(jsPaper["authors"]) >= 1:
                for jsAuthor in jsPaper["authors"]:
                    author = Author()
                    if "last_name" in jsAuthor:
                        author.lastname = jsAuthor["last_name"]
                    if "first_name" in jsAuthor:
                        author.initials = jsAuthor["first_name"]
                    paper.authors.append(author)
                    if "affiliations" in jsPaper:
                        if len(jsAuthor["affiliations"]) > 0:
                            if "address_spec" in jsAuthor["affiliations"][0]:
                                if isinstance(
                                        jsAuthor["affiliations"][0]["address_spec"]["organizations"]["organization"],
                                        list):
                                    len_org = len(
                                        jsAuthor["affiliations"][0]["address_spec"]["organizations"]["organization"])
                                    # write max index - newer (my opinion)
                                    if len_org >= 1:
                                        author.affiliations = \
                                            jsAuthor["affiliations"][0]["address_spec"]["organizations"]["organization"][len_org - 1]["text"]
        paper.keywords = []
        if "keywords" in jsPaper:
            if isinstance(jsPaper["keywords"], list):
                paper.keywords = jsPaper["keywords"]
        paper.num_authors = len(paper.authors)
        papers.append(paper)
        paper.title = re.sub('(\")', '', paper.title)
        paper.title = re.sub('(\')', "", paper.title)
        paper.authors = re.sub('(\")', '', str(paper.authors))
        paper.authors = re.sub('(\')', "", str(paper.authors))
        paper.keywords = re.sub('(\")', '', str(paper.keywords))
        paper.keywords = re.sub('(\')', "", str(paper.keywords))
        values = "'" + str(paper.title) + "', '" + str(paper.authors) + "', " + str(
            paper.num_authors) + ", '" + str(paper.range_pages) + "', '" + str(paper.doi) + "', '" + str(
            paper.year_publ) + "', '" + str(paper.language) + "','" + str(paper.keywords) + "', 'wos'"
        insert(table, columns, values, conn)
        print(pub_count)
        pub_count += 1
