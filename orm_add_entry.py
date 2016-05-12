import psycopg2

try:
    conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='admin'")
except:
    print ("I am unable to connect to the database")
print("Done")
