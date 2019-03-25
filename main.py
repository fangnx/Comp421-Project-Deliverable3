import psycopg2
import datetime
from string import Template
from prettytable import PrettyTable

conn = psycopg2.connect(dbname="cs421", user="cs421g64", password="zhanlang123", host='comp421.cs.mcgill.ca')
cur = conn.cursor()
cur.execute("select tablename from pg_catalog.pg_tables where schemaname='cs421g64'")
TABLES = list(map(lambda x: x[0], cur.fetchall()))


def select_all(table_name):
	query = "select * from " + table_name
	cur.execute(query)
	print(cur.fetchall())

# OPTION 1
def find_trip(stopName, startTimeFrom, startTimeTo, startLocation):
	query = ("select trips.tripId, trips.numberOfSeatsAvailable, trips.price, trips.startTime, trips.title " + "from trips " + "join hasstops h on trips.tripid = h.tripid " + "where h.stopname = '" + stopName + "' and "+  "(trips.starttime between '" + startTimeFrom + "' and '" + startTimeTo + "') and " + "trips.startlocation = '" + startLocation + "' " + "order by price asc;")
	cur.execute(query)
	return cur.fetchall()


# OPTION 2
def cancel_trip():
	# TBD
	pass


# OPTION 3
# OPTION 3-1
def set_driver_status_with_no_cars():
	action = ("update drivers "
			"set status = 'No Car' where username not in "
			"(select owner from vehicles); "
			"select username, driverlicense, status from drivers" )
	cur.execute(action)
	return cur.fetchall()


# OPTION 4 hall of 带明星
# OPTION 4-1
def rank_destination():
	query = ("select cityname, count(tripid) as numbers from hasstops natural join cities group by cityname order by numbers DESC limit 10;")
	cur.execute(query)
	return cur.fetchall()


# OPTION 4-2
def rank_comments():
	query = ("select tripid,title, avg(rating) from comments natural join trips t group by (tripid,title) order by avg DESC limit 10;")
	cur.execute(query)
	return cur.fetchall()


# OPTION 4-3
def rank_vehicles():
	query = ("select model, count(tripid) from leads natural join vehicles group by model order by count DESC limit 10;")
	cur.execute(query)
	return cur.fetchall()


# OPTION 4-4
def rank_users_with_most_trips(startTimeFrom, startTimeTo):
	query = Template("select uid, firstname, lastname, count(b.tripid) as numoftrips from books b "
			"join trips t on b.tripid = t.tripid and "
			"t.starttime between '$startTimeFrom' and '$startTimeTo' "
			"join users u on b.uid = u.username "
			"group by uid, firstname, lastname " 
			"order by count(b.tripid) desc;")
	query_s = query.substitute(startTimeFrom=startTimeFrom, startTimeTo=startTimeTo)
	cur.execute(query_s)
	return cur.fetchall()


# OPTION 5
def find_user_info(firstName, lastName):
	query = Template("select username, firstname, lastname, email, phone from users where firstname = '$firstName' and lastname = '$lastName';")
	query_s = query.substitute(firstName=firstName, lastName=lastName)
	cur.execute(query_s)
	return cur.fetchall()


# OPTION 6-Y
def find_comments_about_trip_by_user(startLocation, firstName, lastName):
	query = Template("select c.commentid, c.content, c.rating, u.firstname, u.lastname, t.title from comments c, users u, trips t "  
			"where c.uid = u.username and c.tripid = t.tripid and u.firstname = '$firstName' and u.lastname = '$lastName' and t.startlocation = '$startLocation' "
			"order by commentid;")
	query_s = query.substitute(startLocation=startLocation, firstName=firstName, lastName=lastName)
	cur.execute(query_s)
	return cur.fetchall()


# OPTION 6-N
def find_comments_about_trip(startLocation):
	query = Template("select c.commentid, c.content, c.rating, t.title from comments c, trips t "  
		"where c.tripid = t.tripid and t.startlocation = '$startLocation' "
		"order by commentid ")
	query_s = query.substitute(startLocation=startLocation)
	cur.execute(query_s)
	return cur.fetchall()

########################################

# Utils functions

def validate_name(name):
	return name.strip()	


def validate_datetime(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		raise ValueError("date time format")


########################################

print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("***************************** WELCOME TO THE CARPOOL DATABASE SYSTEM *****************************")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

while True:
	print("==============================================================================================")
	print("Please Enter One of the Following Options:\n")
	print("\t1. Find a Trip")
	print("\t2. Cancel a Trip")
	print("\t3. Vehicle management")
	print("\t4. Hall of Fame")
	print("\t5. User Information")
	print("\t6. View Comments about a Trip")
	print("\t0. Exit the system\n")
	opt = input("Please Enter Your Choice From 0 To 6: ")
	if not opt.isdigit() or int(opt) > 6 or int(opt) < 0:
		print('throw new InvalidInputException("User must enter a number between 0 and 6.")')
		continue
	
	if int(opt) == 0: # EXIT THE SYSTEM
		break
	
	if int(opt) == 1:
		while True:
			print("==============================================================================================")
			timeStart = input("Please enter the the earliest start time of the trip: ")
			timeEnd = input("Please enter the the lastest start time of the trip: ")
			try:
				validate_datetime(timeStart)
				validate_datetime(timeEnd)
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

	if int(opt) == 3:
		while True:
			print("===============================================================================================")
			print("Please select the action you would like to implement:\n")
			print("\t1. Set the status of Drivers without Vehicles to 'No Car'")
			choice = input("\nEnter Your Choice From 1 to 5: ")

			if int(choice) == 1:
				print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				print("~~~~~~~~~~~~~~~~~~~ Set the status of Drivers without Vehicles to 'No Car' ~~~~~~~~~~~~~~~~~~~~~~~")
				print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
				t = PrettyTable(["User ID", "Driver License", "Status"])
				action_result = set_driver_status_with_no_cars()
				for entry in action_result:
					t.add_row(entry)
				print(t)

			isExit = input("Continue Next Search? [Y/N]: ")
			if isExit.upper() != 'Y' and isExit.upper() != 'N':
				print('throw new InvalidInputException("别像Gunter一样傻逼，输入Y或者n")')
			elif isExit == 'n':
				break


	
	if int(opt) == 4:
		while True:
			print("===============================================================================================")
			print("Please select the rank you would like to see:\n")
			print("\t1. Top 10 Trips with the highest Comments rating")
			print("\t2. Top 10 Trip destinations")
			print("\t3. Top 10 Vehicle model for your ride")
			print("\t4. Top 10 Users with the most Trips in a given time period")
			print("\t5. Top 10 Users")
			choice = input("\nEnter Your Choice From 1 to 5: ")

			if int(choice) == 1:
				print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				print("~~~~~~~~~~~~~~~~~~~~~~ Top 10 Trips with the highest Comments rating ~~~~~~~~~~~~~~~~~~~~~~~~~~")
				print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
				t = PrettyTable(["Trip ID", "Trip title", "Average rating"])
				result = rank_comments()
				for entry in result:
					t.add_row(entry)
				print(t)

			if int(choice) == 2:
				print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Top 10 Trip destinations ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
				t = PrettyTable(["City name", "Number of trips"])
				result = rank_destination()
				for city in result:
					t.add_row(city)
				print(t)

			if int(choice) == 3:
				print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				print("~~~~~~~~~~~~~~~~~~~~~~~~~~~ Top 10 Vehicle models for your ride ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
				t = PrettyTable(["Car Model", "Number of been used in trips"])
				result = rank_vehicles()
				for vehicle in result:
					t.add_row(vehicle)
				print(t)
			
			if int(choice) == 4:
				print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				print("~~~~~~~~~~~~~~~~~~~ Top 10 Users with the most Trips in a given time period ~~~~~~~~~~~~~~~~~~~")
				print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
				# firstName = input("Please enter the first name of the user: ")
				# lastName = input("Please enter the last name of the user: ")
				# if not validate_name(firstName) or not validate_name(lastName):
				# 	print("You must enter a valid non-empty name.")
				# 	continue	
				startTimeFrom = input("Please enter the the earliest start time of the trip: ")
				startTimeTo = input("Please enter the the lastest start time of the trip: ")
				try:
					validate_datetime(startTimeFrom)
					validate_datetime(startTimeTo)
				except ValueError:
					print("You must enter a valid datetime.")
					continue
				
				t = PrettyTable(["User ID", "Fisrt Name", "Last Name", "Number of Trips"])
				query_result = rank_users_with_most_trips(startTimeFrom, startTimeTo)
				for entry in query_result:
					t.add_row(entry)
				print(t)

			isExit = input("Continue Next Search? [Y/N]: ")
			if isExit.upper() != 'Y' and isExit.upper() != 'N':
				print('throw new InvalidInputException("别像Gunter一样傻逼，输入Y或者n")')
			elif isExit == 'n':
				break

	if int(opt) == 5:
		while True:
			print("===============================================================================================")
			print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
			print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Find User information given the name ~~~~~~~~~~~~~~~~~~~~~~~~~~~~")	
			print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")					
			firstName = input("Please enter the first name of the user: ")
			lastName = input("Please enter the last name of the user: ")
			if not validate_name(firstName) or not validate_name(lastName):
				print("You must enter a valid non-empty name.")
				continue

			t = PrettyTable(["User Name", "Fisrt Name", "Last Name", "Email", "Phone Number"])
			query_result = find_user_info(firstName, lastName)
			for entry in query_result:
				t.add_row(entry)
			print(t)

			isExit = input("Continue Next Search? [Y/N]: ")
			if isExit.upper() != 'Y' and isExit.upper() != 'N':
				print('throw new InvalidInputException("别像Gunter一样傻逼，输入Y或者n")')
			elif isExit == 'n':
				break

	if int(opt) == 6: # For testing: Quebec, Naxin, Fang
		while True:
			print("===============================================================================================")
			print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")			
			print("~~~~~ Find Comments given the start location of the Trip & optionally the name of the User ~~~~")
			print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
			startLocation = input("Please enter the start location of the trip: ")
			query_opt = input("Do you want to specify the name of the User who writes the Comment? [Y/N]: ")

			if query_opt.upper() == 'Y':
				firstName = input("Please enter the first name of the user: ")
				lastName = input("Please enter the last name of the user: ")
				if not validate_name(firstName) or not validate_name(lastName):
					print("You must enter a valid non-empty name.")
					continue

				t = PrettyTable(["Comment ID", "Content", "Rating", "First Name", "Last Name", "Trip Description"])
				query_result = find_comments_about_trip_by_user(startLocation, firstName, lastName)
				for entry in query_result:
					t.add_row(entry)
				print(t)

			else:
				t = PrettyTable(["Comment ID", "Content", "Rating", "Trip Description"])
				query_result = find_comments_about_trip(startLocation)
				for entry in query_result:
					t.add_row(entry)
				print(t)
				

			isExit = input("Continue Next Search? [Y/N]: ")
			if isExit.upper() != 'Y' and isExit.upper() != 'N':
				print('throw new InvalidInputException("别像Gunter一样傻逼，输入Y或者n")')
			elif isExit == 'n':
				break
