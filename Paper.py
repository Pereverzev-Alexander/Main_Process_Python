import json
import os
import pprint

# jsonNameSCOPUS = r'C:\Git\Main_Process_Python\scopus.json'
# jsonNameWOS = r'C:\Git\Main_Process_Python\wos.json'
# jsonNameSPIN = r'C:\Git\Main_Process_Python\spin.json'

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
        #volume

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
dir_spin = r'C:\Users\Denis\Desktop\publications\spin'
dir_scopus = r'C:\Users\Denis\Desktop\publications\scopus'
dir_wos = r'C:\Users\Denis\Desktop\publications\wos'
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
                author.initials = jsAuthor["initials"]
                if "affiliations" in jsAuthor:
                    if isinstance(jsAuthor["affiliations"]["affiliation"], dict):
                        author.affiliations = jsAuthor["affiliations"]["affiliation"]["orgname"]
                paper.authors.append(author)
        elif isinstance(jsPaper["authors"]["author"], dict):
                jsAuthor = jsPaper["authors"]["author"]
                author = Author()
                author.lastname = jsAuthor["lastname"]
                author.initials = jsAuthor["initials"]
                if "affiliations" in jsAuthor:
                    if isinstance(jsAuthor["affiliations"]["affiliation"], dict):
                        author.affiliations = jsAuthor["affiliations"]["affiliation"]["orgname"]
                paper.authors.append(author)
        paper.keywords = []
        if "keywords" in jsPaper:
            if isinstance(jsPaper["keywords"]["keyword"], list):
                for jsKeywords in jsPaper["keywords"]["keyword"]:
                    keyword = jsKeywords["text"]
                    paper.keywords.append(keyword)
            elif isinstance(jsPaper["keywords"]["keyword"], dict):
                jsKeywords = jsPaper["keywords"]["keyword"]
                keyword = jsKeywords["text"]
                paper.keywords.append(keyword)
        paper.num_authors = len(paper.authors)
        papers.append(paper)
        pprint.pprint(papers)
    # print(len(papers))
    #  # scanDict(Author.lastname,js, "lastname") - 1 list
    # # scan2Dict(Paper.type, js, ["type"])
    # scan2Dict(Paper.year_publ, js, ["yearpubl"])
    # scanDict(Paper.range_pages, js, "pages")
    # scan2Dict(Paper.doi, js, ["codes", "code", "text"])
    # scan2Dict(Paper.title, js, ["titles", "title", "text"])
    #
    # author = Author()
    # scanDict(author.lastname, js, "lastname")
    # scanDict(author.initials, js, "initials")
    # scan2Dict(author.affiliations, js, ["authors", "author", "affiliations", "affiliation", "orgname"])
    # Paper.authors.append(author)  # list of authors
    #
    # Paper.num_authors = len(author.initials)  # len(Paper.authors)
    # # тоже нужен список
    # scan2Dict(Paper.keywords, js, ["keywords", "keyword", "text"])
    #
    # # pprint.pprint(Paper.type)
    # # print("num_authors=", len(Paper.num_authors))
    # print("title=", len(Paper.title))
    # print("keywords=", len(Paper.keywords))
    # print("year_publ=", len(Paper.year_publ))
    # print("doi=", len(Paper.doi))
    # print("range_pages=", len(Paper.range_pages))
    # print("Initials=", len(author.initials))
    # print("lastname=", len(author.lastname))
    # print("affiliations=", len(author.affiliations))
    # print("authors=", len(Paper.authors), "\n")
    # data_file.close()


# print(Paper.title[100], Paper.keywords[100], Paper.doi[100], Paper.year_publ[100],Paper.range_pages[100])

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




