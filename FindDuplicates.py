from FilterSelectOrm import *
from FindDoiDuplicates import Duplicate, insert_duplicate, insert_internal
from math import ceil
import datetime

def equals_doi(p1,p2):
    if p1.doi == "None" or p1.doi == ""  or p1.doi == "0":
        return False
    if p2.doi == "None" or p2.doi == "" or p2.doi == "0":
        return False
    return p1.doi == p2.doi


def internal_compare_publications(p, comp):
    if equals_doi(p, comp):
        return True
    elif p.title == comp.title:
        return True
    return False


def find_duplicates_internal(pubs1, pubs2, pubs3, duplicates):
    for p in pubs1:
        for comp in pubs2:
            if internal_compare_publications(p, comp):
                insert_duplicate(p, comp, duplicates)
        for comp in pubs3:
            if internal_compare_publications(p, comp):
                insert_duplicate(p, comp, duplicates)


def find_grouping(duplicates):
    year_inf = 1900
    year_sup = 2016
    for year in range(year_inf, year_sup):
        year_min = year - 1
        year_max = year + 1
        pubs_scopus = db_select_year(year_min,year_max,"scopus")
        pubs_wos = db_select_year(year_min, year_max, "wos")
        pubs_spin = db_select_year(year_min, year_max, "spin")
        pubs_scopus_strict = db_select_year(year, year, "scopus")
        pubs_wos_strict = db_select_year(year, year, "wos")
        pubs_spin_strict = db_select_year(year, year, "spin")
        total_len = len(pubs_scopus) + len(pubs_wos) + len(pubs_spin)
        print(year_min,year_max,total_len)
        if total_len < 2:
            continue
        dups = []
        find_duplicates_internal(pubs_scopus_strict, pubs_wos, pubs_spin, dups)
        find_duplicates_internal(pubs_wos_strict, pubs_scopus, pubs_spin, dups)
        find_duplicates_internal(pubs_spin_strict, pubs_wos, pubs_scopus, dups)
        duplicates += dups
        print(len(dups), len(duplicates))




#test
duplicates = []
time_start = datetime.datetime.now()
find_grouping(duplicates)
time_end = datetime.datetime.now()
time_diff = time_end-time_start
print("Time elapsed: "+str(time_diff.seconds)+" s")

