import json
import os
import psycopg2
import re
import time
import pprint
import datetime

class Author:
    lastname = ""
    initials = ""
    affiliations = ""

    def __repr__(self):
        return str(self.lastname) + " " + str(self.initials) + " " + str(self.affiliations)

        # def __init__(self, par1, par2, par3):
        #     self.lastname = par1
        #     super().__init__()


class Paper:
    # id= []
    # type = []
    language = ""
    year_publ = 0
    range_pages = 0
    title = ""
    keywords = []
    doi = 0
    num_authors = 0
    authors = []  # from Author

    def __repr__(self):
        return str(self.keywords) + " " + str(self.year_publ) + " " + str(self.doi) + " " + str(
            self.authors) + " " + str(self.title) + " " + str(self.language) + " " + str(self.num_authors)


def scanDict(data_json, dct, key):
    if isinstance(dct, dict):
        if key in dct.keys():
            data_json.append(dct[key])
            return
        else:
            for x in dct.values():
                scanDict(data_json, x, key)
    elif isinstance(dct, list):
        for x in dct:
            scanDict(data_json, x, key)
    else:
        return


def scanDictSplit(data_json, dct, key):
    if isinstance(dct, dict):
        if key in dct.keys():
            data_json.append(dct[key].split()[0])
            return
        else:
            for x in dct.values():
                scanDictSplit(data_json, x, key)
    elif isinstance(dct, list):
        for x in dct:
            scanDictSplit(data_json, x, key)
    else:
        return


def scan2Dict(data_json, dct, keys):
    if isinstance(dct, dict):
        if len(keys) == 1:
            key = keys[0]
            if key in dct:
                data_json.append(dct[key])
        else:
            if keys[0] in dct:
                scan2Dict(data_json, dct[keys[0]], keys[1:])
    elif isinstance(dct, list):
        for x in dct:
            scan2Dict(data_json, x, keys)
    else:
        return

def IsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

# connect to db
def connect2db(host_name, db_name, user_name, password):
    conn_string = "host='" + host_name + "' dbname='" + db_name + "' user='" + user_name + "' password='" + password + "'"
    conn = psycopg2.connect(conn_string)
    return conn


# insert data to db
def insert(table, columns, values, conn):
    cursor = conn.cursor()
    statement = '''INSERT INTO ''' + table + ''' (''' + columns + ''') VALUES (''' + values + ''')'''
    cursor.execute(statement)
    conn.commit()
    return


# connect to db
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
        # pprint.pprint(papers)

        # if int(paper.year_publ) < 1970:
        #     paper.year_publ = 0
        # else:
        #     paper.year_publ = int(time.mktime(time.strptime(str(paper.year_publ) + "-01-01", '%Y-%m-%d')))
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
                            paper.range_pages = int(range_pages_only_int1) - int(range_pages_only_int0) + 1
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
        # pprint.pprint(papers)

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
        # pprint.pprint(papers)


        # if (tmp_year < 1970):
        #     paper.year_publ = 0
        # else:
        #     paper.year_publ = int(time.mktime(time.strptime(str(paper.year_publ), '%Y-%m-%d')))
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
