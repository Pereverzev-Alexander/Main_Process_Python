import psycopg2

conn_string = "host='localhost' dbname='db' user='postgres' password='pass'"
conn = psycopg2.connect(conn_string)

sql = "select * from publication"
cursor = conn.cursor()
cursor.execute(sql)
records = cursor.fetchall()
print(records)
