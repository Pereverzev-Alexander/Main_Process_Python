from FilterSelectOrm import *
from collections import defaultdict
# list of found duplicates
duplicates = []

# prepare doi hash dictionary
doi_dict = {}
for p in db_select_year_range(0, 3000, "scopus"):
    if p.doi == "":
        continue
    doi_dict[p.doi] = p
for p in db_select_year_range(0, 3000, "wos"):
    if p.doi == "":
        continue
    doi_dict[p.doi] = p
for p in db_select_year_range(0, 3000, "spin"):
    if p.doi == "":
        continue
    doi_dict[p.doi] = p
# now doi_dict contains all unique doi values as keys
# all except invalid

# # number of groups of articles
# # grouped by publication year
# year_partitions = 30
# inf_year = 1970
# sup_year = 2030
# year_step = int((sup_year-inf_year)/year_partitions)
# p_groups_scopus = []
# p_groups_wos = []
# p_groups_spin = []
# for i in range(0, year_partitions):
#     year_min = inf_year + year_step*i
#     year_max = year_min + year_step
#     p_groups_scopus.append(db_select_year_range(year_min, year_max, "scopus"))
#     p_groups_wos.append(db_select_year_range(year_min, year_max, "wos"))
#     p_groups_spin.append(db_select_year_range(year_min, year_max, "spin"))
#     print("add partition "+str(i))
# # add articles with invalid publication year
# p_groups_scopus.append(db_select_year_range(0, 0, "scopus"))
# p_groups_wos.append(db_select_year_range(0, 0, "wos"))
# p_groups_spin.append(db_select_year_range(0, 0, "spin"))


def compare_publications(publ, comp_publ):
    if publ.doi != "" and comp_publ.doi != "":
        # we are able to compare doi
        if publ.doi == comp_publ.doi:
            # articles are duplicates
            return True
        # articles are different because doi differ
        return False
    else:
        # unable to compare doi, use other criteria
        # check pages range
        if publ.range_pages != "" and comp_publ.range_pages != "":
            if publ.range_pages == comp_publ.range_pages:
                # articles are duplicates
                return True
                # articles are different because doi differ
            return False
        else:
            return False


def compare_from_sources(source1, source2, equal_dict):
    cl = db_select_year_range(0, 0, source2)
    i = 0
    for publ in db_select_all(source1):
        i += 1
        print("Compare "+source1+" "+source2+" : "+str(i))
        equal = None
        year = get_publication_year(publ)
        if year > 0:
            comp_list = db_select_year_range(year, year, source2)
            # search in list for matching articles
            # return after first found duplicate
            for comp_publ in comp_list:
                if compare_publications(publ, comp_publ):
                    equal = comp_publ
                    break
        if equal is None:
            # search in list for matching articles
            # return after first found duplicate
            for comp_publ in cl:
                if compare_publications(publ, comp_publ):
                    equal = comp_publ
                    break
        if equal is not None:
            equal_dict[publ].append(equal)


def compare_all():
    dict1 = defaultdict(list)
    dict2 = defaultdict(list)
    dict3 = defaultdict(list)
    compare_from_sources("scopus","wos",dict1)
    print("Compared scopus and wos")
    compare_from_sources("scopus", "spin", dict2)
    print("Compared scopus and spin")
    compare_from_sources("wos", "spin", dict3)
    print("Compared wos and spin")
    # merge dict1 and dict3
    for k in dict1.keys():
        vals = dict1[k]
        for v in vals:
            if v in dict3:
                dict1[k].append(dict3[v])
                del dict3[v]
    # merge dict1 and dict2
    for k in dict2.keys():
        dict1[k].append(dict2[k])
        del dict2[k]
    print(len(dict1.keys()))
    print(len(dict2.keys()))
    print(len(dict3.keys()))

compare_all()






