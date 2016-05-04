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

class Model:
        # id= []
        type= []
        language= []
        year_publ= []
        range_pages= []
        title= []
        keywords= []
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
    data_file = open(path);
    data = data_file.read()
    js = json.loads(data)
    # Author.lastname = scanDict(js, "lastname")
    scanDict(Author.lastname,js, "lastname")
    scanDict(Model.type, js, "type")
    scanDict(Model.year_publ, js, "yearpubl")
    scanDict(Model.range_pages, js, "pages")
    # pprint.pprint(Model.year_publ)
    # print(len(Author.lastname))
    data_file.close()


for x in dirs_scopus:
    path = os.path.join(dir_scopus, x)
    data_file = open(path);
    data = data_file.read()
    js = json.loads(data)
    scanDictSplit(Author.lastname,js, "name")
    scanDict(Model.type, js, "sourceType")
    scanDict(Model.year_publ, js, "pubDate")
    scanDict(Model.range_pages, js, "pageRange")
    # pprint.pprint(Author.lastname)
    # print(len(Author.lastname))
    data_file.close()

for x in dirs_wos:
    path = os.path.join(dir_wos, x)
    data_file = open(path);
    data = data_file.read()
    js = json.loads(data)
    scanDict(Author.lastname,js, "last_name")
    scanDict(Model.type, js, "heading")
    scanDict(Model.year_publ, js, "pub_date")
    scanDict(Model.range_pages, js, "page_range")
    # pprint.pprint(Author.lastname)
    # print(len(Author.lastname))
    data_file.close()

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



# def scan2Dict(dct, keys):
#     if isinstance(dct, dict):
#         if len(keys) == 1:
#             initials.append(dct[keys[0]])
#         else:
#             scanDict(dct[keys[0]], keys[1:])
#     elif isinstance(dct, list):
#         for x in dct:
#             scanDict(x, keys)
#     else:
#         return

#scan2Dict(js, ["authors", "author", 'initials'])

