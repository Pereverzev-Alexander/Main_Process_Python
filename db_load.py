# Модуль для заполнения базы данных данными, полученными из JSON - строк
import json
import os
import re
import datetime
from DbInteractions import Publication,db_drop_duplicates


def normalize_page_range_publication(range_pages_str):
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
            if range_pages_only_int0.isdigit():
                return int(range_pages_only_int0)
    else:
        return 1


def open_json_file(dir_json, curr_json):
    path = os.path.join(dir_json, curr_json)
    data_file = open(path)
    data = data_file.read()
    return json.loads(data)


def load_json_scopus_in_db(dir_json):
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
            else:
                publication.year_publ = 0
            if "language" in jsPaper:
                publication.language = jsPaper["language"]
            else:
                publication.language = ""
            if "pageRange" in jsPaper:
                publication.range_pages = normalize_page_range_publication(jsPaper["pageRange"])
            if "doi" in jsPaper:
                publication.doi = jsPaper["doi"]
            else:
                publication.doi = ""
            if "titleEn" in jsPaper:
                jsTitle = jsPaper["titleEn"]
                if (jsTitle != "") or (jsTitle != "null"):
                    publication.title = jsPaper["titleEn"]
                elif "titleRu" in jsPaper:
                    publication.title = jsPaper["titleRu"]
            else:
                publication.title = ""
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
            publication.source = "scopus"
            publication.save()
            count += 1
            print(count)
    return count


def load_json_spin_in_db(dir_json):
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
                publication.range_pages = normalize_page_range_publication(jsPaper["pages"])
            if "codes" in jsPaper:
                if isinstance(jsPaper["codes"]["code"], dict):
                    jsDoi = jsPaper["codes"]["code"]
                    if jsDoi["type"] == "DOI":
                        publication.doi = jsDoi["text"]
            if publication.doi is None:
                publication.doi = ""
            if "titles" in jsPaper:
                if isinstance(jsPaper["titles"]["title"], dict):
                    if isinstance(jsPaper["titles"]["title"]["text"], str):
                        publication.title = jsPaper["titles"]["title"]["text"]
            if publication.title is None:
                        publication.title = ""
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
            publication.source = "spin"
            publication.save()
            print(count)
            count += 1
    return count


def load_json_wos_in_db(dir_json):
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
                publication.range_pages = normalize_page_range_publication(jsPaper["page_range"])
            if "doi" in jsPaper:
                publication.doi = jsPaper["doi"]
            else:
                publication.doi = ""
            if "title_en" in jsPaper:
                publication.title = jsPaper["title_en"]
            else:
                publication.title = ""
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
            publication.source = "wos"
            publication.save()
            print(count)
            count += 1
    return count


def db_drop_publications():
    # clear duplicates table
    db_drop_duplicates()
    Publication.drop_table(True)
    Publication.create_table()
    print("Publications table created")


# main part
db_drop_publications()
count_spin = load_json_spin_in_db(r'publications\spin')
count_scopus = load_json_scopus_in_db(r'publications\scopus')
count_wos = load_json_wos_in_db(r'publications\wos')
print("Articles uploaded to the database ", str(count_scopus + count_spin + count_wos))
