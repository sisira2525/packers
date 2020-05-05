from flask import Flask, render_template, redirect, url_for , flash
import MySQLdb
import base64
import re
from flask import request
from passlib.hash import pbkdf2_sha256
import datetime
import time
import os

app = Flask(__name__)

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'FeB1st@2k'
app.config['MYSQL_DB'] = 'Packers'
app.secret_key = 'my unobvious secret key'


conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd = 'FeB1st@2k',port = 3306,db="Packers")
cursor = conn.cursor()
custid = ""
CARID = ""
payment_type = ""
payment_status = ["Paid","Not Paid"]
b_actual_id = 0

def checkstring(inputstring):
	F = 0
	length = len(inputstring)
	for a in range(0,length):
		if (inputstring[a] >= 'a' and inputstring[a] <= 'z') or (inputstring[a] >= 'A' and inputstring[a] <= 'Z'):
			F = 1
		else:
			F = 0
	if F == 1:
		return False
	else:
		return True
	
#-----------------------------------------------FRONT PAGE -------------------------------------------------------
@app.route("/",methods=['GET','POST'])

def homepage():
	print("ENTERED")
	return render_template("index.html")
#---------------------------ADD New CUSTOMER ----------------------------------------------------------------------------

@app.route('/addcustomer/',methods = ['GET','POST'])

def register():
	
	print("entered")
	return render_template('addcustomer.html')
	

@app.route('/adduser/',methods = ['GET','POST'])

def adduser():
	print("entered")
	Username_to_string1 = ""
	flag = False

	cursor = conn.cursor()
	secret_key = '1234567890123456'
	try:
		current_day = ""
		current_month = ""
		current_year = "" 
		current = datetime.datetime.now()
		current_day = str(current.day)
		current_month = str(current.month)
		current_year = str(current.year)
		current_date3 = current_day + "-" + current_month + "-" + current_year
		#Username_to_string1 = ""
		fname = request.form["FName"]
		value1 = checkstring(fname)
		if value1 == True:
			flash("Please enter a Valid First Name !!!")
			return render_template("addcustomer.html")
		
		lname = request.form["lName"]
		value2 = checkstring(lname)
		if value2 == True:
			flash("Please enter a Valid Last Name !!!")
			return render_template("addcustomer.html")
		username= request.form["username"]
		cursor.execute("""SELECT userId FROM Cust_User """)
		actual_usernames1 = cursor.fetchall()
		list1 = list(actual_usernames1)
		Username_to_string1 = str(username)
		length = len(list1)
		for a in range(0,length):
			print(actual_usernames1[a])
			print(Username_to_string1)
			if actual_usernames1[a][0] == Username_to_string1:
				print(actual_usernames1[a])
				print(Username_to_string1)
				flag = True
		print(Username_to_string1)
		print(list1)
		print(flag)
		if flag == True:
			flash("Sorry Username is Already Present !!!")
			return render_template("addcustomer.html")
		else:
			email = request.form["email"]
			if re.search('@',email):
				em=0
			else:
				flash("Please Enter Valid Email  !!!")
				return render_template("addcustomer.html")	
			phone = request.form["PhoneNumber"]
			plen = len(phone)
			if plen != 10:
				flash("Please Enter Valid mobile Number only !!!")
				return render_template("addcustomer.html")
			age = request.form["age"]
			int_age = int(age)
			if int_age < 18 :
				flash("Sorry you must above 18 years of age !!!")
				return render_template("addcustomer.html")	
			password = request.form["Password"]
			cpassword = request.form["ConfirmPassword"]
			if password==cpassword:
				print("Matched")
			else:
				flash("Passwords in both the fields did not match.")
				return render_template("addcustomer.html")
			hash_password = pbkdf2_sha256.hash(password)					# Hashing + salting Password
			
			cursor.execute("""INSERT INTO Cust_User(userId,fName,lName,emailId,phone,registration_Date,password) VALUES (%s,%s,%s,%s,%s,%s,%s)""",(username,fname,lname,email,phone,current_date3,hash_password)) 
				
				
			flash("Successfully Registered !!! You can book a cab now!!! ")
			return redirect('/login')
	except Exception as e:
		return(str(e))
			
			
			
#---------------------------------------END------------------------------------------------------

#-------------------------------------LOGIN PAGE--------------------------------------------------------
@app.route('/login')

def signin():
	print("entered")
	return render_template('signin.html')
	
	
@app.route('/echo',methods=['POST'])

def sign():
	Cinflag = False
	cust_password_match = False
	current_day = ""
	current_month = ""
	current_year = "" 
	current = datetime.datetime.now()
	current_day = str(current.day)
	current_month = str(current.month)
	current_year = str(current.year)
	current_date4 = current_day + "-" + current_month + "-" + current_year
	print("entered")
	cursor = conn.cursor()
	Username_to_string = ""
	Username = request.form['Username']
	Password = request.form['Password']
	cursor.execute("""SELECT userId FROM Cust_User """)
	cust_actual_usernames = cursor.fetchall()
	cust_actual_usernames_list = list(cust_actual_usernames)
	cust_length = len(cust_actual_usernames_list)
	Username_to_string1 = Username
	print(cust_actual_usernames)
	for a in range(0,cust_length):
		if cust_actual_usernames_list[a][0] == Username_to_string1:
			Cinflag = True	
			
	if Cinflag == True:
		print("CUSTUser is present")
		cursor.execute("""SELECT password FROM Cust_User WHERE userId =%s""",[Username])
		cust_actual_password = cursor.fetchone()
		cust_password_match = pbkdf2_sha256.verify(Password,cust_actual_password[0])
	

	if cust_password_match == True:
		current_time = time.strftime("%X")
		cursor.execute("""INSERT INTO Login_History(userId,Date,Time) values(%s,%s,%s)""",(Username,current_date4,current_time))
		conn.commit()
		global custid
		custid = Username[:]
		flash("Login Sucessfull, Now Book a Cab !!!")
		return render_template("booking.html")
	elif Username=='ADMIN' and pbkdf2_sha256.verify(Password,pbkdf2_sha256.hash('ROOT')):
		return render_template("adminpage.html")
	else:
		flash("Invalid Credentials")
		return render_template("signin.html")

#--------------------------------------------BOOKING PAGE-----------------------------------------------------

@app.route('/booking/',methods = ['GET','POST'])
def bookingdriver():
	
	print("entered")
	#booking()
	return render_template('booking.html')
	
	
@app.route('/bookingNow/',methods = ['GET','POST'])


def booking():
	print("entered")
	cabs_list = ['Mini Van','Eicher','Lorry']
	buflag = False
	try:
		cab_route = ['Coimbatore-Bangalore','Coimbatore-Erode','Coimbatore-Chennai','Coimbatore-Madurai','Coimbatore-Ernakulam']
		car_empty = False
		userId=request.form["userId"]
		cursor.execute("""SELECT userId FROM Cust_User""")
		busernames = cursor.fetchall()
		busernames_list = list(busernames)
		busernames_len = len(busernames_list)
		for a in range(0,busernames_len):
			if busernames_list[a][0] == userId:
				buflag = True
		if buflag == False:
			flash("Entered Username does not Exist !!!")
			return render_template('booking.html')
		
		#userId = userId.encode(userId.originalEncoding)
		cursor.execute("""SELECT fName,lName,emailId,phone FROM Cust_User WHERE userId = %s""",[userId])
		custinfo = cursor.fetchall()
		custinfo_list = list(custinfo)
		print(custinfo_list)
		fname = custinfo_list[0][0]
		lname = custinfo_list[0][1]
		email = custinfo_list[0][2]
		phone = custinfo_list[0][3]
		print(fname,lname,email,phone)
		cab1 = request.form["cab"]
		cab = int(cab1)
		print(userId,fname,lname,phone,email,cab)
		cab_name = ""
		route = ""
		cab_name = cabs_list[cab]
		startDate = request.form["startDate"]
		endDate = request.form["endDate"]
		time = request.form["time"]
		carroute = int(request.form["route"])
		route = cab_route[carroute]
		pickupLocation = request.form["pickupLocation"]
		dropoffLocation = request.form["dropoffLocation"]
		pricePerKm = 10
		car_name = cabs_list[cab]
		print('car_name'+car_name)
		cursor.execute("""SELECT Car_id FROM Car WHERE status_car = 'Available' and model_name like %s""",[car_name])
		car = cursor.fetchall()
		if len(car)>0:
			print('Structure is not empty.')
			car_empty = False
		else:
			print('Structure is empty.')
			return redirect('/allbooked')
		print("CAR NAME ",car)
		carid = car[0][0]
		print(carid)
		
		global CARID
		CARID = carid[:]
		bookingId=userId+str(datetime.datetime.now())
		print(bookingId,userId,cab_name,startDate,endDate,time,pickupLocation,dropoffLocation,carid,route)
		cursor.execute("""select price_per_km from Car WHERE Car_id = %s""",[carid])
		amt=cursor.fetchall()
		print(amt)
		amt=amt[0][0]
		amt*=20
		cursor.execute("""INSERT INTO Booking(bookingId,userId,Cab,startDate,endDate,Pickup_time,Pickup_location,Drop_off_location,carid,cab_route,total_amount) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",[bookingId,userId,cab_name,startDate,endDate,time,pickupLocation,dropoffLocation,carid,route,(int(amt))]) 
		cursor.execute("""UPDATE Car SET status_car = 'Booked' WHERE Car_id = %s""",[carid])
		conn.commit()
		global b_actual_id
		cursor.execute("""select bookingId from Booking where Pickup_time=%s and startDate=%s """,[time,startDate])
		b_id=cursor.fetchall()
		b_actual_id=b_id[0][0]
		print(b_actual_id)	
		return redirect("/lastpage")		
	except Exception as e:
		return(str(e))
#--------------------------------------------------BOOKING PAGE ENDS------------------------------------------------------------------------------

#------------------------------------------------DISPLAY BOOKING ------------------------------------------------------------------

@app.route("/displaybooking/",methods=['GET','POST'])

def displaybooking():
	cursor = conn.cursor()
	cursor.execute("""SELECT * FROM Booking""")
	data5 = cursor.fetchall()
	cursor.close()
	
	return render_template("displaybooking.html",data = data5)
	
#--------------------------------------------DISPLAY BOOKING END--------------------------------------------------------------------
#--------------------------------------------ADMIN PAGE -------------------------------------------------------------
@app.route('/adminpage/',methods=['GET','POST'])

def adminpage():
	print("Entered")
	return render_template("adminpage.html")
#---------------------------------END ADMIN PAGE-----------------------------------------------

#----------------------------------LOGIN HISTORY----------------------------------------------
@app.route("/logindetails/",methods=['GET','POST'])

def logindetails():
	cursor = conn.cursor()
	cursor.execute("""SELECT * FROM Login_History""")
	data5 = cursor.fetchall()
	cursor.close()
	
	return render_template("loginhistory.html",data = data5)


#-----------------------------------Display Customer Details----------------------------
@app.route("/displaycustomer/",methods=['GET','POST'])

def displaycustomer():
	cursor = conn.cursor()
	cursor.execute("""SELECT * FROM Cust_User""")
	data1 = cursor.fetchall()
	cursor.close()
	
	return render_template("displaycustomers.html",data = data1)
#-------------------------------------DELETE CUSTOMER USER-----------------------------------------------------------------------------
@app.route("/deleteuser/",methods=['GET','POST'])

def deleteuserdriver():
	return render_template("deleteuser.html")	
	
@app.route("/deleteUSER/",methods=['GET','POST'])

def deleteuser():
	cursor = conn.cursor()
	dusername1 = str(request.form["dusername"])
	
	udflag = False
	cursor.execute("""SELECT userId FROM Cust_User""")
	usernamesud = cursor.fetchall()
	usernames_listud = list(usernamesud)
	usernames_lenud = len(usernames_listud)
	for a in range(0,usernames_lenud):
		if usernames_listud[a][0] == dusername1:
			udflag = True
	if udflag == False:
		flash("Entered Username does not Exist !!!")
		return render_template("deleteuser.html")
		
	cursor.execute("""DELETE FROM Cust_User WHERE userId = %s""",[dusername1])
	conn.commit()
	cursor.close()
	flash("Customer Successfully Deleted !!!")
	return render_template("deleteuser.html")
	
#------------------------------DELETE CUSTOMER ENDS --------------------------------------------------------------------------------

#----------------------------------ADD NEW CAR -----------------------------------------------------------------------------------------------

@app.route("/addcar/",methods=['GET','POST'])

def addcardriver():
	return render_template("addcar.html")

@app.route("/addCAR/",methods=['GET','POST'])

def addcarform():
	cursor = conn.cursor()
	carid = str(request.form["carid"])
	model = request.form["model"]
	registration = request.form["registration"]
	seating = request.form["seating"]
	price = int(request.form["price"])
	status='Available'
	cursor.execute("""INSERT INTO Car(Car_id,model_name,registeration_no,ton_capacity,price_per_km,status_car) VALUES (%s,%s,%s,%s,%s,%s)""",(carid,model,registration,seating,price,status)) 
	conn.commit()
	cursor.close()
	flash("New Car Successfully Added !!!")
	return render_template("addcar.html")
	
#-----------------------------------ADD CAR ENDS---------------------------------------------------------------------------------

#------------------------------------------------DISPLAY CARS-----------------------------------------------------------------------------

@app.route("/displaycars/",methods=['GET','POST'])

def displaycars():
	cursor = conn.cursor()
	cursor.execute("""SELECT * FROM Car""")
	data2 = cursor.fetchall()
	cursor.close()
	
	return render_template("displaycars.html",data = data2)
#--------------------------------------------DISPLAY CAR ENDS-------------------------------------------------------------------------------

#---------------------------------------------DELETE CAR----------------------------------------------------------------------------------

@app.route("/deletecars/",methods=['GET','POST'])

def deletecardriver():
	return render_template("deletecars.html")	
	
@app.route("/deleteCARS/",methods=['GET','POST'])

def deletecar():
	cursor = conn.cursor()
	carid = str(request.form["carid"])
	
	cflag = False
	cursor.execute("""SELECT Car_id FROM Car""")
	carids = cursor.fetchall()
	carid_list = list(carids)
	carid_list_len = len(carid_list)
	for a in range(0,carid_list_len):
		if carid_list[a][0] == carid:
			cflag = True
	if cflag == False:
		flash("Entered CarId does not Exist !!!")
		return render_template("deletecars.html")
		
	cursor.execute("""DELETE FROM Car WHERE Car_id = %s""",[carid])
	conn.commit()
	cursor.close()
	flash("Car Successfully Deleted !!!")
	return render_template("deletecars.html")
	

#-----------------------------------------------------------------------

#----------------------------ABOUT PAGE-------------------------------------------

@app.route('/aboutpage/',methods=['GET','POST'])

def aboutpage():
	print("Entered") 	#Testing
	
	return render_template("about.html")	
	
#--------------------------END ABOUT PAGE -------------------------------------------------------------------------	
	
#---------------------DISPLAY CAR STATUS ---------------------------------------

@app.route("/displaycarstatus/",methods=['GET','POST'])

def carstatusdriver():
	cursor = conn.cursor()
	cursor.execute("""SELECT Car_id,model_name,registeration_no,status_car FROM Car""")
	data1 = cursor.fetchall()
	cursor.close()
	
	return render_template("displaystatuscar.html",data = data1)

#---------------------DISPLAY CAR STATUS ENDS---------------------------------------.

#---------------------Change CAR STATUS ---------------------------------------
@app.route("/changecarstatus/",methods=['GET','POST'])

def changecarstatusdriver():
	return render_template("changecarstatus.html")

@app.route("/changecarSTATUS/",methods=['GET','POST'])

def changecarstatus():
	ccflag = False
	status_type = ['Available','Booked']
	Car_Type = ""
	cursor = conn.cursor()
	carid1 = request.form["cari"]
	
	cursor.execute("""SELECT Car_id FROM Car WHERE Car_id = %s""",[carid1])
	cid = cursor.fetchall()
	cid_list = list(cid)
	cid_len = len(cid_list)
	for a in range(0,cid_len):
		if cid_list[a][0] == carid1:
			ccflag = True
	if ccflag == False:
		flash("Entered CarID is Invalid !!!")
		return render_template("changecarstatus.html")
			
	Type = int(request.form["status"])
	status_Type = status_type[Type]
	
	cursor.execute("""UPDATE Car SET status_car = %s WHERE Car_id = %s""",(status_Type,carid1))
	conn.commit()
	cursor.close()
	#print(mpassword,dusername,husername)
	flash("Car Status Successfully Changed !!!")
	return render_template("changecarstatus.html")


#------------------------------------------------STATUS PAGE--------------------------------------------------
@app.route('/status/',methods=['GET','POST'])

def statusdriver():
	most_used_route = ""
	cursor = conn.cursor()
	cursor.execute("""SELECT COUNT(*) FROM Cust_User""")
	total_c = cursor.fetchall()
	total_cust = total_c[0][0]
	cursor.execute("""SELECT COUNT(*) FROM Car""")
	total_ca = cursor.fetchall()
	total_car1 = total_ca[0][0]
	cursor.execute("""SELECT COUNT(*) FROM Car WHERE status_car = 'Available' """)
	cart = cursor.fetchall()
	tcar = cart[0][0]
	cursor.execute("""SELECT COUNT(*) FROM Booking""")
	tbook = cursor.fetchall()
	tbooking = tbook[0][0]
	cursor.execute("""SELECT COUNT(*) FROM Booking WHERE cab_route = 'Coimbatore-Erode' """)
	NP = cursor.fetchall()
	NProute = int(NP[0][0])
	cursor.execute("""SELECT COUNT(*) FROM Booking WHERE cab_route = 'Coimbatore-Ernakulam' """)
	NN = cursor.fetchall()
	NNroute = int(NN[0][0])
	cursor.execute("""SELECT COUNT(*) FROM Booking WHERE cab_route = 'Coimbatore-Madurai' """)
	NM = cursor.fetchall()
	NMroute = int(NM[0][0])
	cursor.execute("""SELECT COUNT(*) FROM Booking WHERE cab_route = 'Coimbatore-Bangalore' """)
	NA = cursor.fetchall()
	NAroute = int(NA[0][0])
	cursor.execute("""SELECT COUNT(*) FROM Booking WHERE cab_route = 'Coimbatore-Chennai' """)
	ND = cursor.fetchall()
	NDroute = int(ND[0][0])
	if NProute > NNroute and NProute > NMroute and NProute > NAroute and NProute > NDroute:
		most_used_route = "Coimbatore-Erode"
	elif NNroute > NProute and NNroute > NMroute and NNroute > NAroute and NNroute > NDroute:
		most_used_route = "Coimbatore-Ernakulam"
	elif NMroute > NNroute and NMroute > NProute and NMroute > NAroute and NMroute > NDroute:
		most_used_route = "Coimbatore-Madurai"
	elif NAroute > NNroute and NAroute > NMroute and NAroute > NProute and NAroute > NDroute:
		most_used_route = "Coimbatore-Bangalore"
	elif NDroute > NNroute and NDroute > NMroute and NDroute > NAroute and NDroute > NProute:
		most_used_route = "Coimbatore-Chennai"
	
	cursor.execute("""SELECT SUM(total_amount) FROM Booking""")
	total_sum = cursor.fetchall()
	tsum = int(total_sum[0][0])	
	print("TOTAL CUST",total_cust)
	return render_template('Status.html',total = total_cust,tcar=total_car1,total_car = tcar,total_booking=tbooking,mroute=most_used_route,total_sum1=tsum)

@app.route('/allbooked/',methods=['GET','POST'])
def allbooked():
	return render_template("allbooked.html")


@app.route('/booked/',methods=['GET','POST'])
def booked():
	return redirect("/")
	
	
@app.route('/lastpage/',methods=['GET','POST'])

def lastpage():
	return render_template("final.html")
	
if __name__ == "__main__":
	
	app.run(debug=True)	
	