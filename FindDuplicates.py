from FilterSelectOrm import *
import datetime
import translite
import re
from fuzzywuzzy import fuzz


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

    def insert(self, publication):
        if publication.source == "scopus":
            self.scopus_p = publication
        elif publication.source == "wos":
            self.wos_p = publication
        else:
            self.spin_p = publication

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

    def get_scopus_id(self):
        if self.scopus_p is not None:
            return self.scopus_p.id
        return None

    def get_wos_id(self):
        if self.wos_p is not None:
            return self.wos_p.id
        return None

    def get_spin_id(self):
        if self.spin_p is not None:
            return self.spin_p.id
        return None


# class to store all duplicates
# does fast insertion
class DuplicatesStorage:
    duplicates = []
    id_dict = {}

    # insert new publication in duplicates list
    def insert(self, publication, duplicate):
        # check if this publication is already duplicate
        if duplicate.id in self.id_dict:
            # get index of duplicate entry in list
            index = self.id_dict[duplicate.id]
            # add publication to duplicate entry
            self.duplicates[index].insert(publication)
            # add new id key to registered duplicates
            self.id_dict[publication.id] = index
        elif publication.id in self.id_dict:
            # get index of duplicate entry in list
            index = self.id_dict[publication.id]
            # add publication to duplicate entry
            self.duplicates[index].insert(duplicate)
            # add new id key to registered duplicates
            self.id_dict[duplicate.id] = index
        else:
            # create new duplicate
            d = Duplicate()
            d.insert(publication)
            d.insert(duplicate)
            self.duplicates.append(d)
            # save index of entry in duplicates list in dictionary
            self.id_dict[publication.id] = len(self.duplicates)-1


def equals_doi(p1,p2):
    if p1.doi == "None" or p1.doi == "" or p1.doi == "0":
        return False
    if p2.doi == "None" or p2.doi == "" or p2.doi == "0":
        return False
    return p1.doi == p2.doi


def internal_compare_titles(title1, title2):
    t1 = re.sub("[- :.,]", "", title1).lower()
    t2 = re.sub("[- :.,]", "", title2).lower()
    return t1 == t2


def internal_compare_publications(p, comp):
    if equals_doi(p, comp):
        return True
    elif p.title == comp.title:
        return True
    elif p.num_authors == comp.num_authors:
        len1 = len(p.title)
        len2 = len(comp.title)
        len_diff = abs(len1 - len2)
        if len_diff > 5:
            return False

        if internal_compare_titles(p.title, comp.title):
            return True
        else:
            # ratio = fuzz.ratio(p.title, comp.title)
            # if ratio > 90:
            #     print("Fuzzy match","ratio", ratio,"\n", p.title,"\n", comp.title)
            #     return True
            return False

    return False


def find_duplicates_internal(pubs1, pubs2, pubs3, duplicates):
    for p in pubs1:
        for comp in pubs2:
            if internal_compare_publications(p, comp):
                duplicates.insert(p, comp)
        for comp in pubs3:
            if internal_compare_publications(p, comp):
                duplicates.insert(p, comp)


def compare_second_name_author(pub1, pub2):
    first_author = pub1.authors[0:pub1.authors.find(' ')]
    second_author = pub2.authors[0:pub2.authors.find(' ')]
    first_author = translite.transliterate(first_author.lower())
    second_author = translite.transliterate(second_author.lower())
    if first_author == second_author:
        return True
    else:
        return False


def find_grouping(duplicates):
    year_inf = 1860
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
        print("Check years",year_min,year_max,"Total articles:",total_len)
        if total_len < 2:
            continue
        find_duplicates_internal(pubs_scopus_strict, pubs_wos, pubs_spin, duplicates)
        find_duplicates_internal(pubs_wos_strict, pubs_scopus, pubs_spin, duplicates)
        find_duplicates_internal(pubs_spin_strict, pubs_wos, pubs_scopus, duplicates)
        print("Total ducplicates:", len(duplicates.duplicates))






#test
storage = DuplicatesStorage()
time_start = datetime.datetime.now()
find_grouping(storage)
time_end = datetime.datetime.now()
time_diff = time_end-time_start
print("Time elapsed: "+str(time_diff.seconds)+" s")
db_load_duplicates(storage)
print("Duplicates loaded to database")




