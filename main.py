import psycopg2
import datetime
from prettytable import PrettyTable
from string import Template

conn = psycopg2.connect(dbname="cs421", user="cs421g64", password="zhanlang123", host='comp421.cs.mcgill.ca')
cur = conn.cursor()

cur.execute("select tablename from pg_catalog.pg_tables where schemaname='cs421g64'")
TABLES = list(map(lambda x: x[0], cur.fetchall()))


def select_all(table_name):
    query = "select * from " + table_name
    cur.execute(query)
    print(cur.fetchall())


def select_most_expensive_trip():
    query = ("select trips.* from trips " + "where price >= all (select price from trips)")
    cur.execute(query)
    print(cur.fetchall()[0])


# def find_trip_by_startlocation(startLocation):
#     query = ("select trips.* from trips
#             "where startlocation = " startLocation)
#     cur.execute(query)


def find_trip(stopName, startTimeFrom, startTimeTo, startLocation):
    query = ("select trips.tripId, trips.numberOfSeatsAvailable, trips.price, trips.startTime, trips.title " + "from trips " + "join hasstops h on trips.tripid = h.tripid " + "where h.stopname = '" + stopName + "' and "+  "(trips.starttime between '" + startTimeFrom + "' and '" + startTimeTo + "') and " + "trips.startlocation = '" + startLocation + "' " + "order by price asc;")
    cur.execute(query)
    return cur.fetchall()


def find_user_info(firstName, lastName):
	query("select username, firstname, lastname, email, phone from users where firstname = '" + firstName + "' and lastname = '" + lastName + "'")
	cur.execute(query)
	return cur.fetchall()






def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("date time format")


select_most_expensive_trip()
print("WELCOME TO THE CARPOOL DATABASE SYSTEM")

while True:
    print("==============================================================================================")
    print("Please Enter the Following Option: ")
    print("1. Find a Trip")
    print("2. Cancel a Trip")
    print("3. Vehicle management")
    print("4. Hall of Fame")
    print("5. User Information")
    print("6. View Comments about a Trip")
    print("0. Exit the system")
    opt = input("Please enter your choice in 0-6: ")
    if not opt.isdigit() or int(opt) > 6 or int(opt) < 0:
        print('throw new InvalidInputException("User must enter a number between 0 and 6.")')
        continue
    if int(opt) == 0:
        break
    if int(opt) == 1:
        while True:
            print("==============================================================================================")
            timeStart = input("Please enter the the earliest start time of the trip: ")
            timeEnd = input("Please enter the the lastest start time of the trip: ")
            try:
                validate(timeStart)
                validate(timeEnd)
            except ValueError:
                print('throw new InvalidInputException("User must enter a valid datetime format.")')
                continue
            startLocation = input("Please enter the start location of the trip; it should be a city: ")
            stopName = input("Please enter the end location of the trip; it should be a stop: ")
            t = PrettyTable(['ID', 'Seat', 'Price', 'Start Time', 'Title'])
            for entry in find_trip(stopName, timeStart, timeEnd, startLocation):
                t.add_row(entry)
            print(t)
            isExit = input("Continue Next Search? [Y/N]: ")
            if isExit.upper() != 'Y' and isExit.upper() != 'N':
                print('throw new InvalidInputException("别像Gunter一样傻逼，输入Y或者n")')
            elif isExit == 'n':
                break

	# if int(opt) == 5:
	# 	while True:
	# 		print("==============================================================================================")
