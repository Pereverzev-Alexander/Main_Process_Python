from FilterSelectOrm import *

# find all articles with same doi
doi_dict = {}
same_doi_publ = []
# insert all articles from scopus, use doi as key
for p in db_select_all("scopus"):
    if p.doi == "":
        continue
    doi_dict[p.doi] = ("scopus",p.id)
# try to insert articles from wos
for p in db_select_all("wos"):
    if p.doi == "":
        continue
    if p.doi in doi_dict:
        same_doi_publ.append(p)
    else:
        doi_dict[p.doi] = ("wos", p.id)
# try to insert articles from spin
for p in db_select_all("spin"):
    if p.doi == "":
        continue
    if p.doi in doi_dict:
        same_doi_publ.append(p)
    else:
        doi_dict[p.doi] = ("spin", p.id)


for o in same_doi_publ:
    print(o.title, o.source, o.doi)
print("\nFound total  DOI duplicates: "+str(len(same_doi_publ)))