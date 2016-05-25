from FilterSelectOrm import db_select_year_range

# find articles with the same count author
def find_same_num_authors(year_min, year_max, source1, source2):
    lst = []
    lst_1 = db_select_year_range(year_min, year_max, source1)
    lst_2 = db_select_year_range(year_min, year_max, source2)
    for p1 in lst_1:
        for p2 in lst_2:
            if p1.num_authors == p2.num_authors:
                lst.append((p1,p2))
    return lst

# returns all articles published within given range
# from given sources with same pages range
def find_same_pages(year_min, year_max, source1, source2):
    lst = []
    lst_1 = db_select_year_range(year_min, year_max, source1)
    lst_2 = db_select_year_range(year_min, year_max, source2)
    for p1 in lst_1:
        for p2 in lst_2:
            if p1.range_pages == p2.range_pages:
                lst.append((p1,p2))
    return lst

# test function
list_pub = find_same_num_authors(2001, 2001, "spin", "wos")
print("Found with same count authors: "+str(len(list_pub)))

list_pub = find_same_pages(2000, 2000, "scopus", "wos")
print("Found with same pages range: "+str(len(list_pub)))
