from FindDuplicates import DuplicatesStorage
from FindDuplicates import find_grouping
from FindDuplicates import db_load_duplicates
import datetime


# find duplicates
storage = DuplicatesStorage()
time_start = datetime.datetime.now()
find_grouping(storage)
time_end = datetime.datetime.now()
time_diff = time_end-time_start
print("Time elapsed: "+str(time_diff.seconds)+" s")
# load result to Postgres
db_load_duplicates(storage)
print("Duplicates loaded to database")
count_triples = storage.get_triples_count()
# show statistics
print("In 3 databases: " + str(count_triples))
count_scopus_wos = storage.get_count_sources("scopus","wos")
count_scopus_spin = storage.get_count_sources("scopus","spin")
count_spin_wos = storage.get_count_sources("spin","wos")
print("In Scopus and WoS: " +str(count_scopus_wos))
print("In Scopus and Spin: " +str(count_scopus_spin))
print("In Spin and WoS: " +str(count_spin_wos))
