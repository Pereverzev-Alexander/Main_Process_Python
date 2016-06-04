from FindDuplicates import find_grouping
from FindDuplicates import db_recreate_duplicates
from DbInteractions import db_count_excluding,db_count_duplicates,db_count_triples
import datetime


# find duplicates
db_recreate_duplicates()
time_start = datetime.datetime.now()
find_grouping()
time_end = datetime.datetime.now()
time_diff = time_end-time_start
print("Time elapsed: "+str(time_diff.seconds)+" s")
# show statistics
print("Total duplicates found: ",db_count_duplicates())
print("Duplicates found in 3 databases: ",db_count_triples())
print("Duplicates found in Scopus and WoS: ",db_count_excluding("spin"))
print("Duplicates found in Scopus and Spin: ",db_count_excluding("wos"))
print("Duplicates found in Spin and WoS: ",db_count_excluding("scopus"))

