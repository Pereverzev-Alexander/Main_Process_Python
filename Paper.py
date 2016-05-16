import json
import os
import pprint

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
        #type = []
        language = ""
        year_publ = 0
        range_pages = ""
        title = ""
        keywords = []
        doi = 0
        num_authors = 0
        authors = [] #from Author


        def __repr__(self):
            return str(self.keywords) + " " + str(self.year_publ) + " " + str(self.doi) + " " + str(self.authors) + " " + str(self.title)+ " " + str(self.language)+ " " + str(self.num_authors)



def scanDict(data_json,dct, key):
            if isinstance(dct, dict):
                if key in dct.keys():
                    data_json.append(dct[key])
                    return
                else:
                    for x in dct.values():
                        scanDict(data_json,x, key)
            elif isinstance(dct, list):
                for x in dct:
                    scanDict(data_json,x, key)
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
    for jsPaper in js:
        paper = Paper()
        if "yearpubl" in jsPaper:
                paper.year_publ=jsPaper["yearpubl"]
        if "language" in jsPaper:
            paper.language = jsPaper["language"]
        if "pages" in jsPaper:
            paper.range_pages = jsPaper["pages"]
        if "codes" in jsPaper:
            if isinstance(jsPaper["codes"]["code"], dict):
                jsDoi = jsPaper["codes"]["code"]
                if jsDoi["type"] == "DOI":
                    paper.doi = jsDoi["text"]
        if "titles" in jsPaper:
            if isinstance(jsPaper["titles"]["title"],dict):
                if isinstance(jsPaper["titles"]["title"]["text"],str):
                     paper.title = jsPaper["titles"]["title"]["text"]
        paper.authors = []
        if isinstance(jsPaper["authors"]["author"],list):
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
        if "language" in jsPaper:
            paper.language = jsPaper["language"]
        if "pageRange" in jsPaper:
            paper.range_pages = jsPaper["pageRange"]
        if "doi" in jsPaper:
            paper.doi = jsPaper["doi"]
        if "titleEn" in jsPaper:
            jsTitle = jsPaper["titleEn"]
            if (jsTitle != "") or (jsTitle != "null"):
                paper.title = jsPaper["titleEn"]
            elif "titleRu" in jsPaper:
                paper.title = jsPaper["titleRu"]
        paper.authors = []
        #maybe have more authers such as student, unkonownInternal
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
        paper.keywords = []
        if "keywords" in jsPaper:
            keyword = jsPaper["keywords"]
            paper.keywords.append(keyword)
        paper.num_authors = len(paper.authors)
        papers.append(paper)
        # pprint.pprint(papers)


for x in dirs_wos:
    path = os.path.join(dir_wos, x)
    data_file = open(path)
    data = data_file.read()
    js = json.loads(data)
    papers = []
    for jsPaper in js:
        paper = Paper()
        if "pub_date" in jsPaper:
                paper.year_publ=jsPaper["pub_date"]
        if "static_data" in jsPaper:
            if isinstance(jsPaper["static_data"]["fullrecord_metadata"], dict):
                if isinstance(jsPaper["static_data"]["fullrecord_metadata"]["languages"]["language"], dict):
                    if isinstance(jsPaper["static_data"]["fullrecord_metadata"]["languages"]["language"], dict):
                        paper.language = jsPaper["static_data"]["fullrecord_metadata"]["languages"]["language"]["text"]
        if "page_range" in jsPaper:
            paper.range_pages = jsPaper["page_range"]
        if "doi" in jsPaper:
            paper.doi = jsPaper["doi"]
        if "title_en" in jsPaper:
            paper.title = jsPaper["title_en"]
        paper.authors = []
        if isinstance(jsPaper["authors"],list):
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
                                if isinstance(jsAuthor["affiliations"][0]["address_spec"]["organizations"]["organization"], list):
                                    len_org = len(jsAuthor["affiliations"][0]["address_spec"]["organizations"]["organization"])
                                    # write max index - newer (my opinion)
                                    if len_org >= 1:
                                        author.affiliations = jsAuthor["affiliations"][0]["address_spec"]["organizations"]["organization"][len_org-1]["text"]
        paper.keywords = []
        if "keywords" in jsPaper:
            if isinstance(jsPaper["keywords"], list):
                    paper.keywords = jsPaper["keywords"]
        paper.num_authors = len(paper.authors)
        papers.append(paper)
        # pprint.pprint(papers)

# for x in dirs_scopus:
#     path = os.path.join(dir_scopus, x)
#     data_file = open(path);
#     data = data_file.read()
#     js = json.loads(data)
#     # scanDict(Paper.type, js, "sourceType")
#     scanDict(Paper.year_publ, js, "pubDate")
#     scanDict(Paper.range_pages, js, "pageRange")
#
#     author = Author()
#     scanDictSplit(Author.lastname,js, "name")
#
#     # pprint.pprint(Author.lastname)
#     # print(len(Author.lastname))
#     data_file.close()

# for x in dirs_wos:
#     path = os.path.join(dir_wos, x)
#     data_file = open(path);
#     data = data_file.read()
#     js = json.loads(data)
#     scanDict(Author.lastname,js, "last_name")
#     scanDict(Paper.type, js, "heading")
#     scanDict(Paper.year_publ, js, "pub_date")
#     scanDict(Paper.range_pages, js, "page_range")
#     # pprint.pprint(Author.lastname)
#     # print(len(Author.lastname))
#     data_file.close()

# open json file
# data_file = open(jsonNameSPIN)
# data = data_file.read()
# js = json.loads(data)

#search keys
# pprint.pprint(js[0].keys())
# # pprint.pprint(js[1].keys())
# for key, value in js[0]["authors"]["author"][0].items():
#     print(key)
#     #print(key, value)

# lastname = scanDict(js, "lastname")
# pprint.pprint(data_json)




