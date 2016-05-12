import json
import os
import pprint

# jsonNameSCOPUS = r'C:\Git\Main_Process_Python\scopus.json'
# jsonNameWOS = r'C:\Git\Main_Process_Python\wos.json'
# jsonNameSPIN = r'C:\Git\Main_Process_Python\spin.json'

class Author:
        lastname = []
        initials = []
        affiliations = []
        # def __init__(self, par1, par2, par3):
        #     self.lastname = par1
        #     super().__init__()

class Paper:
        # id= []
        type = []
        language = []
        year_publ = []
        range_pages = []
        title = []
        keywords = []
        doi = []
        num_authors = []
        authors = [] #from Author
        #volume??



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
    # print(path)
    data_file = open(path)
    data = data_file.read()
    js = json.loads(data)
    #scanDict(Author.lastname,js, "lastname") - 1 list
    scan2Dict(Paper.type, js, ["type"])
    scan2Dict(Paper.year_publ, js, ["yearpubl"])
    scanDict(Paper.range_pages, js, "pages")
    scan2Dict(Paper.doi, js, ["codes", "code", "text"])
    scan2Dict(Paper.title, js, ["titles", "title", "text"])


    author = Author()
    scanDict(author.lastname, js, "lastname")
    scanDict(author.initials, js, "initials")
    scan2Dict(author.affiliations, js, ["authors", "author", "affiliations","affiliation","orgname"])
    Paper.authors.append(author) #list of authors

    Paper.num_authors=len(author.initials)#len(Paper.authors)
    #тоже нужен список
    scan2Dict(Paper.keywords, js, ["keywords", "keyword", "text"])

    # pprint.pprint(Paper.title)
    # print("num_authors=", len(Paper.num_authors))
    print("title=", len(Paper.title))
    print("keywords=", len(Paper.keywords))
    print("year_publ=",len(Paper.year_publ))
    print("Type=", len(Paper.type))
    print("doi=", len(Paper.doi))
    print("range_pages=", len(Paper.range_pages))
    print("Initials=",len(author.initials))
    print("lastname=",len(author.lastname))
    print("affiliations=",len(author.affiliations))
    print("authors=",len(Paper.authors),"\n")
    data_file.close()


# for x in dirs_scopus:
#     path = os.path.join(dir_scopus, x)
#     data_file = open(path);
#     data = data_file.read()
#     js = json.loads(data)
#     scanDictSplit(Author.lastname,js, "name")
#     scanDict(Model.type, js, "sourceType")
#     scanDict(Model.year_publ, js, "pubDate")
#     scanDict(Model.range_pages, js, "pageRange")
#     # pprint.pprint(Author.lastname)
#     # print(len(Author.lastname))
#     data_file.close()

# for x in dirs_wos:
#     path = os.path.join(dir_wos, x)
#     data_file = open(path);
#     data = data_file.read()
#     js = json.loads(data)
#     scanDict(Author.lastname,js, "last_name")
#     scanDict(Model.type, js, "heading")
#     scanDict(Model.year_publ, js, "pub_date")
#     scanDict(Model.range_pages, js, "page_range")
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




