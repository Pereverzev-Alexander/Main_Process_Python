import json
import Translit
import Translate

jsonNameSCOPUS = 'scopus_0.json'
jsonNameWOS = 'wos_0.json'
jsonNameSPIN = 'spin_19xx-1995_org_items_192.json'

with open(jsonNameSCOPUS) as data_file:
    data = json.load(data_file)
    data_file.close()

print("Count objects: %i" % len(data))

i = 0
for key in data:
    if i < 9:
        print("Object: %s" % key)
        i += 1
    else:
        print("To much output!")
        break
print("Done!")

print(Translit.transliterate(u"ЮЛЯ Тестинг Первозванский"))
print(Translate.translateString(u"ЮЛЯ Тестинг Тестинг"))
