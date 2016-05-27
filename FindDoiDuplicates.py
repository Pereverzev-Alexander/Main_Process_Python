from FilterSelectOrm import *


# class to store found duplicates
class Duplicate:
    def __str__(self):
        res = "duplicate: "
        if self.scopus_p is not None:
            res += " scopus: " + str(self.scopus_p.id)
        if self.wos_p is not None:
            res += " wos: " + str(self.wos_p.id)
        if self.spin_p is not None:
            res += " spin: " + str(self.spin_p.id)
        return res

    def __repr__(self):
        res = "repr: "
        return res

    scopus_p = None
    wos_p = None
    spin_p = None

    def count_instances(self):
        count = 0
        if self.scopus_p is not None:
            count += 1
        if self.wos_p is not None:
            count += 1
        if self.spin_p is not None:
            count += 1
        return count


# insert internal function
def insert_internal(p, duplicate):
    if p.source == "scopus":
        duplicate.scopus_p = p
        return
    if p.source == "wos":
        duplicate.wos_p = p
        return
    if p.source == "spin":
        duplicate.spin_p = p


# insert article into respective Duplicate class
def insert_duplicate(p, dupl_p, dupl_list):
    if p.source == dupl_p.source:
        print("Trying to insert duplicate from same source")
        return
    for d in dupl_list:
        if dupl_p.source == "scopus" and d.scopus_p is not None and d.scopus_p.id == dupl_p.id:
            insert_internal(p, d)
            return
        if dupl_p.source == "wos" and d.wos_p is not None and d.wos_p.id == dupl_p.id:
            insert_internal(p, d)
            return
        if dupl_p.source == "spin" and d.spin_p is not None and d.spin_p.id == dupl_p.id:
            insert_internal(p, d)
            return
    # another duplicate not found, insert new one
    d = Duplicate()
    insert_internal(p, d)
    insert_internal(dupl_p, d)
    dupl_list.append(d)


def compare_pages(publication, list1, list2):
    if publication.range_pages != "":
        for comp_p in list1:
            if comp_p.range_pages == publication.range_pages:
                return comp_p
        for comp_p in list2:
            if comp_p.range_pages == publication.range_pages:
                return comp_p
    return None


def compare_titles(publication, list1, list2):
    if publication.title == "":
        return None
    for comp_p in list1:
        if comp_p.title.lower() == publication.title.lower():
            return comp_p
    for comp_p in list2:
        if comp_p.title.lower() == publication.title.lower():
            return comp_p
    return None


# # find all articles with same doi
# doi_dict = {}
# duplicates = []
# list_scopus = db_select_all("scopus")
# list_wos = db_select_all("wos")
# list_spin = db_select_all("spin")
#
# i = 0
# # insert all articles from scopus, use doi as key
# for p in list_scopus:
#     i += 1
#     print(i, len(duplicates))
#     if p.doi == "":
#         continue
#     doi_dict[p.doi] = p
#
# # try to insert articles from wos
# for p in list_wos:
#     i += 1
#     print(i, len(duplicates))
#     if p.doi == "":
#         c = compare_titles(p, list_scopus, list_spin)
#         if c is not None:
#             insert_duplicate(p, c, duplicates)
#         continue
#     if p.doi in doi_dict:
#         insert_duplicate(p, doi_dict[p.doi], duplicates)
#     else:
#         doi_dict[p.doi] = p
#
# # try to insert articles from spin
# for p in list_spin:
#     i += 1
#     print(i, len(duplicates))
#     if p.doi == "":
#         c = compare_titles(p, list_scopus, list_wos)
#         if c is not None:
#             insert_duplicate(p, c, duplicates)
#         continue
#     if p.doi in doi_dict:
#         insert_duplicate(p, doi_dict[p.doi], duplicates)
#     else:
#         doi_dict[p.doi] = p
#
#
# # test
# print("\nFound total  DOI duplicates: "+str(len(duplicates)))
# count_double = 0
# count_triple = 0
# for d in duplicates:
#     c = d.count_instances()
#     if c == 2:
#         count_double += 1
#     if c == 3:
#         count_triple += 1
#
# print("In 2 databases: "+str(count_double)+", In 3 databases: "+str(count_triple)+", Total: "+str(count_double+count_triple))
