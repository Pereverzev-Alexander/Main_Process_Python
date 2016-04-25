import json
import os
import pprint

jsonNameSCOPUS = r'C:\Git\Main_Process_Python\scopus.json'
jsonNameWOS = r'C:\Git\Main_Process_Python\wos.json'
jsonNameSPIN = r'C:\Git\Main_Process_Python\spin.json'

class Author:
        lastname = ""
        initials = ""
        affiliations = ""
        # def __init__(self, par1, par2, par3):
        #     self.lastname = par1
        #     super().__init__()

class Model:
        id= ""
        type= ""
        language= ""
        year_publ= ""
        range_pages= ""
        title= ""
        keywords= ""
        #volume??

#перебор файлов в директории, path - ссылка на каждый файл
# dirs = os.listdir(dir)
# for x in dirs:
#     path = os.path.join(dir, x)


#open json file
data_file = open(jsonNameSPIN)
data = data_file.read()
js = json.loads(data)

#search keys
# pprint.pprint(js[0].keys())
# # pprint.pprint(js[1].keys())
# for key, value in js[0]["authors"]["author"][0].items():
#     print(key)
#     #print(key, value)

data_json = []

def scanDict(dct, key):
    if isinstance(dct, dict):
        if key in dct.keys():
            data_json.append(dct[key])
            return
        else:
            for x in dct.values():
                scanDict(x, key)
    elif isinstance(dct, list):
        for x in dct:
            scanDict(x, key)
    else:
        return


scanDict(js, "lastname")
print(data_json)


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

data_file.close()