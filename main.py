import psycopg2

conn = psycopg2.connect(dbname="cs421", user="cs421g64", password="zhanlang123", host='comp421.cs.mcgill.ca')
cur = conn.cursor()

cur.execute("select tablename from pg_catalog.pg_tables where schemaname='cs421g64'")
TABLES = list(map(lambda x: x[0], cur.fetchall()))


def user_interface():
	print("WELCOME TO THE CARPOOL DATABASE SYSTEM")
	option = input("Enter the option: ")


def select_all(table_name: str):
	query = "select * from " + table_name
	cur.execute(query)
	print(cur.fetchall())


def select_most_expensive_trip():
	query = ("select trips.* from trips "
			"where price >= all (select price from trips)")
	cur.execute(query)
	print(cur.fetchall()[0]) 
	

if __name__ == "__main__":
	# user_interface()

	select_most_expensive_trip()
	conn.close()

          