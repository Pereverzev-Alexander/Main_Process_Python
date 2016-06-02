from FindDuplicates import DuplicatesStorage
from FindDuplicates import find_grouping
from FindDuplicates import db_load_duplicates
import datetime


storage = DuplicatesStorage()
time_start = datetime.datetime.now()
find_grouping(storage)
time_end = datetime.datetime.now()
time_diff = time_end-time_start
print("Time elapsed: "+str(time_diff.seconds)+" s")
db_load_duplicates(storage)
print("Duplicates loaded to database")
