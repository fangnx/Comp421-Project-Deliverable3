import psycopg2
import datetime
from string import Template
from prettytable import PrettyTable

conn = psycopg2.connect(dbname="cs421", user="yma67", password="xPR7ri6I", host='comp421.cs.mcgill.ca')
cur = conn.cursor()
cur.execute("select tablename from pg_catalog.pg_tables where schemaname='cs421g64'")
TABLES = list(map(lambda x: x[0], cur.fetchall()))

RED_START = "\33[31m"
GREEN_START = "\33[32m"
YELLOW_START = "\33[33m"
BLUE_START = "\33[34m"
VIOLET_START = "\33[35m"
LBLUE_START = "\33[36m"
BLINK_START = "\33[5m"
COLOR_END = "\33[0m"


class InvalidInputException(Exception): 
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


# OPTION 1
def find_trip(stopName, startTimeFrom, startTimeTo, startLocation):
	query = ("select trips.tripId, trips.numberOfSeatsAvailable, trips.price, trips.startTime, trips.title " + "from trips " + "join hasstops h on trips.tripid = h.tripid " + "where h.stopname = '" + stopName + "' and "+  "(trips.starttime between '" + startTimeFrom + "' and '" + startTimeTo + "') and " + "trips.startlocation = '" + startLocation + "' " + "order by price asc;")
	cur.execute(query)
	return cur.fetchall()


# OPTION 2-1
def view_trip(uname): 
	try: 
		cur.execute("select * from Passengers where userName = '" + uname + "'; ")
	except Exception as e: 
		raise InvalidInputException("Cannot find passenger with name" + uname + ".")
	if len(cur.fetchall()) < 1: 
		raise InvalidInputException("Cannot find passenger with name" + uname + ".")
	try: 
		query = ("select t.title, t.startlocation, t.startTime from Books b, Trips t where t.tripId = b.tripId and b.uid = '" + uname + "'; ")
	except Exception: 
		raise InvalidInputException("Cannot find book with name" + uname + ".")
	cur.execute(query)
	return cur.fetchall()


# OPTION 2-2
def cancel_trip(uname, tripId):
	if not tripId.isdigit(): 
		raise InvalidInputException("Trip id must be a non-negative integer.")
	try: 
		cur.execute("select * from Passengers where userName = '" + uname + "'; ")
	except Exception as e: 
		raise InvalidInputException(e)
	if len(cur.fetchall()) < 1: 
		raise InvalidInputException("Cannot find passenger with name" + uname + ".")
	try:
		query = ("delete from Books where tripId = " + tripId + " and uid = '" + uname + "'; ")
	except Exception: 
		raise InvalidInputException("Cannot delete book with name" + uname + ".")
	cur.execute(query)
	conn.commit()


# OPTION 3
# # OPTION 3-1
# # !!! PROBLEM !!!
# def set_driver_status_with_no_cars():
# 	action = ("update drivers "
# 			"set status = 'No Car' where username not in "
# 			"(select owner from vehicles); ")
# 	query = ("select username, driverlicense, status from drivers;" )
# 	cur.execute(action)
# 	conn.commit()
# 	cur.execute(query)
# 	return cur.fetchall()


# OPTION 3-1
def delete_all_expired_cards():
	action = ("delete from holdcards where cardnumber = "
			"(select cardnumber from creditcards where expirydate < current_date); ")
	query =	("select cardnumber, username from holdcards;")
	cur.execute(action)
	conn.commit()
	cur.execute(query)
	return cur.fetchall()

# OPTION 3-2
def standardize_trip_names():
	action = ("update trips set title = 'Trip from ' || CAST(startLocation AS TEXT) || ' at ' || CAST(startTime AS TEXT) || ' with ' || CAST (numberOfSeatsAvailable AS TEXT) || ' seats';")
	query = ("select tripid, title from trips;")
	cur.execute(action)
	conn.commit()
	cur.execute(query)
	return cur.fetchall()

# OPTION 4
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


# OPTION 4-5
def rank_drivers_with_most_trips(startTimeFrom, startTimeTo):
	query = Template("select uid, firstname, lastname, count(l.tripid) as numoftrips from leads l "
			"join trips t on l.tripid = t.tripid and "
			"t.starttime between '$startTimeFrom' and '$startTimeTo' "
			"join users u on l.uid = u.username "
			"group by uid, firstname, lastname " 
			"order by count(l.tripid) desc;")
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

print(YELLOW_START + "")
print("**************************** WELCOME TO THE CARPOOL DATABASE SYSTEM ***************************")
print("" + COLOR_END)

while True:
	print("===============================================================================================")
	print(GREEN_START + "Please Enter One of the Following Options:\n")
	print("\t1. Find a Trip")
	print("\t2. Trip Management")
	print("\t3. Status Management")
	print("\t4. \"Hall of Fame\" -- List of Useful Rankings")
	print("\t5. User Information")
	print("\t6. View Comments about a Trip" + COLOR_END)
	print(RED_START + "\t0. Exit the System"  + COLOR_END)
	opt = input(GREEN_START + "\nPlease Enter Your Choice From 0 To 6: " + COLOR_END)
	if not opt.isdigit() or int(opt) > 6 or int(opt) < 0:
		print(RED_START + "Invalid Choice. Please Enter Your Choice Again From 0 to 6"  + COLOR_END)
		continue
	
	if int(opt) == 0: # EXIT THE SYSTEM
		print(YELLOW_START + "")
		conn.close()
		print("*************************************** SEE YOU AGAIN! ****************************************")
		print("" + COLOR_END)
		break
	
	if int(opt) == 1:	
		while True:
			print(GREEN_START + "==============================================================================================")
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
			for entry in find_trip(stopName.strip(), timeStart.strip(), timeEnd.strip(), startLocation.strip()):
				t.add_row(entry)
			print(t)
			isExit = input(RED_START + "Continue Next Search? [Y/N]: " + COLOR_END)
			if isExit.upper() != 'Y' and isExit.upper() != 'N':
				print('Must Enter a Y or N')
			elif isExit.upper() == 'N':
				break
		continue
		
	if int(opt) == 2:
		while True: 
			print("===============================================================================================")
			print(GREEN_START + "Please select the rank you would like to see:\n")
			print("\t1. My Trips")
			print("\t2. Cancel a Trip")
			print(RED_START + "\t0. Exit")
			choice = input(GREEN_START + "\nEnter Your Choice From 0 to 2: " + COLOR_END)
			if int(choice) == 0:
				break
			if not choice.isdigit() or int(choice) > 2 or int(choice) < 0:
				print('throw new InvalidInputException("User must enter a number between 0 and 2.")')
				continue
			if int(choice) == 1: 
				uname = input("Please enter your user name: ")
				try: 
					t = PrettyTable(["Title", "Start Location", "Start Time"])
					for entry in view_trip(uname.strip()): 
						t.add_row(entry)
					print(t)
					continue
				except Exception as e: 
					print(e)
					continue
			if int(choice) == 2: 
				uname = input("Please enter your user name: ")
				tripId = input("Please enter the trip id of the trip you want to delete: ")
				try: 
					cancel_trip(uname.strip(), tripId.strip())
				except Exception as e: 
					print(e)
					continue
			isExit = input(RED_START + "Continue Next Round? [Y/N]: " + COLOR_END)
			if isExit.upper() != 'Y' and isExit.upper() != 'N':
				print('Must Enter a Y or N')
			elif isExit.upper() == 'N':
				break
		continue



	if int(opt) == 3:
		while True:
			print("===============================================================================================")
			print(GREEN_START + "Please select the action you would like to implement:\n")
			# print("\t1. Set the status of Drivers without Vehicles to 'No Car'")
			print("\t1. Delete all expired Cards")
			print("\t2. Standardize all Trip names")
			print(RED_START + "\t0. Exit")
			choice = input(GREEN_START + "\nEnter Your Choice From 0 to 2: " + COLOR_END)
			if not choice.isdigit() or int(choice) > 2 or int(choice) < 0:
				print(RED_START + "Invalid Choice. Please Enter Your Choice Again" + COLOR_END)
				continue

			if int(opt) == 0:
				break

			# if int(choice) == 1:
			# 	print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
			# 	print("~~~~~~~~~~~~~~~~~~~~ Set the status of Drivers without Vehicles to 'No Car' ~~~~~~~~~~~~~~~~~~~")
			# 	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
			# 	t = PrettyTable(["User ID", "Driver License", "Status"])
			# 	action_result = set_driver_status_with_no_cars()
			# 	for entry in action_result:
			# 		t.add_row(entry)
			# 	print(t)

			if int(choice) == 1:
				print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Delete all expired Cards ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
				t = PrettyTable(["Card Number", "User ID"])
				action_result = delete_all_expired_cards()
				for entry in action_result:
					t.add_row(entry)
				print("After deletion:\n")
				print(t)

			if int(choice) == 2:
				print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Standardize Trip naming ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
				t = PrettyTable(["Trip ID", "Trip Description"])
				action_result = standardize_trip_names()
				for entry in action_result:
					t.add_row(entry)
				print("After standardization:\n")
				print(t)
				conn.commit()

			isExit = input(RED_START + "Continue Next Action? [Y/N]: " + COLOR_END)
			while (isExit.upper() != 'Y' and isExit.upper() != 'N'):
				isExit = input(RED_START + "Invalid input. Please Enter [Y/N]: " + COLOR_END)
			if isExit.upper() == 'N':
				break
		continue

	if int(opt) == 4:
		while True:
			print("===============================================================================================")
			print(GREEN_START + "Please select the rank you would like to see:\n")
			print("\t1. Top 10 Trips with the highest Comments rating")
			print("\t2. Top 10 Trip destinations")
			print("\t3. Top 10 Vehicle models for your ride")
			print("\t4. Top 10 Users with the most Trips in a given time period")
			print("\t5. Top 10 Drivers with the most Trip in a given time period")
			print(RED_START + "\t0. Exit")
			choice = input(GREEN_START + "\nEnter Your Choice From 0 to 5: " + COLOR_END)
			if not choice.isdigit() or int(choice) > 5 or int(choice) < 0:
				print(RED_START + "Invalid Choice. Please Enter Your Choice Again From 0 to 5" + COLOR_END)
				continue

			if int(opt) == 0: # EXIT THE SYSTEM
				break

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

			if int(choice) == 5:
				print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				print("~~~~~~~~~~~~~~~~~~ Top 10 Drivers with the most Trip in a given time period ~~~~~~~~~~~~~~~~~~")
				print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
				startTimeFrom = input("Please enter the the earliest start time of the trip: ")
				startTimeTo = input("Please enter the the lastest start time of the trip: ")
				try:
					validate_datetime(startTimeFrom)
					validate_datetime(startTimeTo)
				except ValueError:
					print("You must enter a valid datetime.")
					continue
				
				t = PrettyTable(["Driver ID", "Fisrt Name", "Last Name", "Number of Trips"])
				query_result = rank_users_with_most_trips(startTimeFrom, startTimeTo)
				for entry in query_result:
					t.add_row(entry)
				print(t)

			isExit = input(RED_START + "Continue Next Search? [Y/N]: " + COLOR_END)
			while (isExit.upper() != 'Y' and isExit.upper() != 'N'):
				isExit = input(RED_START + "Invalid input. Please Enter [Y/N]: " + COLOR_END)
			if isExit.upper() == 'N':
				break
		continue

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

			isExit = input(RED_START + "Continue Next Search? [Y/N]: " + COLOR_END)
			while (isExit.upper() != 'Y' and isExit.upper() != 'N'):
				isExit = input(RED_START + "Invalid input. Please Enter [Y/N]: " + COLOR_END)
			if isExit.upper() == 'N':
				break
		continue

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

			isExit = input(RED_START + "Continue Next Search? [Y/N]: " + COLOR_END)
			while (isExit.upper() != 'Y' and isExit.upper() != 'N'):
				isExit = input(RED_START + "Invalid input. Please Enter [Y/N]: " + COLOR_END)
			if isExit.upper() == 'N':
				break
		continue