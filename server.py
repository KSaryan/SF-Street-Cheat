from jinja2 import StrictUndefined
from flask import jsonify
from flask import (Flask, render_template, redirect, request, flash,
                   session, url_for)
# from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import update
from model import (Location, Cleaning, Day, User, Side, 
                   Street, FaveLocation, MessageToSend, 
                   Towing, Tow_Location, Tow_Side, connect_to_db, db)
import json
# from datetime import datetime, timedelta, date
import bcrypt
import pytz
import requests
import re

import os
from helpers import *
from math import radians, cos, sin, asin, sqrt
from operator import itemgetter
from decimal import Decimal



app = Flask(__name__)
app.secret_key = "ABC"

@app.route('/')
def homepage():
    """Displays homepage with login form"""
    
    if 'login' in session:
        return redirect ('/parking')
    else:
        return render_template('homepage.html')


@app.route('/logout')
def log_out():
    """logs out user"""

    del session['login']

    return redirect ('/')


@app.route('/login')
def log_in():
    """Displays login page"""

    if 'login' in session:
        return redirect('/parking')
    else:
        return render_template('login.html')


@app.route('/verify_user', methods=["POST"])
def verify_user():
    """Verifies users email and password"""

    password = request.form.get("password")
    email = request.form.get("email")
    email = email.lower()
    q = db.session.query(User).filter(User.email==email).first()
    if q:
        password = password.encode('utf8') 
        hashedpass = q.password.encode('utf8') 
        if bcrypt.checkpw(password, hashedpass):
            session['login'] = q.user_id
            return redirect('/parking')
        else:
            flash("Username or password not found")
            return redirect ('/')

    else:
        flash("Username or password not found")
        return redirect ('/')


@app.route('/create_user', methods=["POST"])
def create_user():
    """Creates new user in database"""

    password = request.form.get("new_password").rstrip()
    password = password.encode('utf8') 
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    email = request.form.get("new_email").rstrip()
    email = email.lower()
    phone = request.form.get("new_number")
    if phone:
        phone = re.sub(r"[\-\(\)\.\s]+", "", phone)

    if db.session.query(User).filter(User.email==email).first():
        flash('There is already an email associated with this account. Please login.')
        return redirect('/login')
    else:
        if len(email) > 30:
            flash('Password or email too long')
            return redirect('/login')
        if phone:
            if len(phone) != 10:
                flash("Invalid number. Make sure to include area code.")
                return redirect('/login')

    user = User(password=hashed, email=email, phone=phone)
    db.session.add(user)
    db.session.commit()
    session['login']= user.user_id
    return redirect('/parking')


@app.route('/user_info')
def display_user_information():
    """displays user information"""

    if 'login' in session:
        user = User.query.get(session['login'])
        return render_template('user_info.html', user=user)
    else:
        flash("Please login in to view")
        return redirect ('/login')


@app.route('/update_user', methods=["POST"])
def update_user_info():
    """Updates User Information"""

    email = request.form.get("email")
    password = request.form.get("password")
    number = request.form.get("number")
    user = User.query.get(session['login'])
    if email:
        if len(email) > 30:
            flash('Password or email too long')
        else:
            email = email.lower()
            user.email = email.rstrip()
            password = password.rstrip()
            password = password.encode('utf8') 
            hashed = bcrypt.hashpw(password, bcrypt.gensalt())
            user.password = hashed
            flash('Information Updated')
            
    
    if number:
        number=re.sub(r"[\-\(\)\.\s]+", "", number)
        if len(number) != 10:
            flash("Invalid number. Make sure to include area code.")
        else:
            user.phone = number.rstrip()
            flash('Information Updated')
        
    
    db.session.add(user)
    db.session.commit()

    return redirect('/user_info')


@app.route('/parking')
def parking():
    """Allows user to submit new parking information"""

    streets = Street.query.order_by(Street.street_name.asc()).all()
    sides = Side.query.all()
    if 'login' in session:
        user = User.query.get(session['login']) 
        email = user.email
    else:
        email = None
    return render_template('parking.html', streets=streets, sides=sides, email=email)


@app.route('/street_cleaning.json')
def street_cleaning():
    """Returns time until street cleaning"""

    address = request.args.get("address")
    address = int(address)
    street = (request.args.get("street")).replace("-", " ")
    side = request.args.get("side")
    geolocation = find_geolocation(address, street)

    towing_locs = get_towing_locs(address, street)
    towings = get_towings(towing_locs)
    towing_message = get_towing_message(towings)

    if side == " " or side == None:
        location = find_location(address, street)
    else:
        location = find_location(address,street, side)
    if location:
        if 'login' in session:
            add_fave_location(session['login'], location.loc_id, 'las', address)


        street_cleanings = Cleaning.query.filter(Cleaning.loc_id==location.loc_id).all()

        holiday = check_for_holidays(street_cleanings)

        if holiday is None:
            holiday = ""

        next_cleaning = return_next_cleaning(street_cleanings)
        if next_cleaning[0] == "now":
            result = {"info_message": next_cleaning[0], 
                      "message": next_cleaning[1] + "/n" + holiday,
                      "geolocation": geolocation,
                      "towing": towing_mesage}

        else:
            result = {"info_message": next_cleaning[0], 
                      "message": next_cleaning[1] + "\n" + holiday,
                      "cleaning_time":next_cleaning[2],
                      "geolocation": geolocation,
                      "towing": towing_message}
    else:
        message = "Not a valid address or no street cleaning in area (Russian Hill)"
        result = {"info_messge": "not a valid address",
                  "message": message,
                  "geolocation": geolocation}


    return jsonify(result)


@app.route('/current_location.json')
def get_current_location():
    """use reverse geolocation to get nearest address"""

    lat = request.args.get("lat")
    lng = request.args.get("lng")
    url = "http://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&sensor=true"%(lat, lng)

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        street = (data["results"][0]["address_components"][1]["short_name"]).upper()
        address= re.sub(r'\-\d+', "", data["results"][0]["address_components"][0]["long_name"])
        sides = get_sides_for_this_location(street, address)
        street = street.replace(" ", "-")
        address_info = {'street': street,
                        'address': address,
                        'sides': sides
                        }
    return jsonify(address_info)


@app.route('/find_sides.json')
def find_sides():
    """returns sides of street associated with an address"""

    address = request.args.get("address")
    street = request.args.get("street")
    street = street.replace("-", " ")
    sides = get_sides_for_this_location(street, address)
    if sides:
        sides_json = {'sides': sides
                     }
        return jsonify(sides_json)
    else:
        return "no sides"


@app.route('/send_text.json', methods=["POST"])
def send_text():
    """Creates a new message in the MessagesToSend table"""

    user = User.query.get(session["login"])
    if user.phone:
        time = request.form.get("cleaningtime")
        message = MessageToSend(user_id=session['login'], time= time)
        db.session.add(message)
        db.session.commit()
        result = {'info_message': 'True',
                   'number': user.phone}
        return jsonify(result)
    else:
        flash("You must have a phone number to get texts")
        result = {'info_message': 'False'}
        return jsonify(result)


@app.route('/nearby_cleanings.json')
def find_nearby_cleanings():
    """returns nearby street cleanings with information needed for creating markers"""

    address = int(request.args.get("address"))
    street = (request.args.get("street")).replace("-", " ")
    side = request.args.get("side")
    closest_places = find_nearby_places(address, street, side)
    #replacing loc_id with message about when street cleaning is
    for place in closest_places:
        loc_id = place[2]
        street_cleanings = Cleaning.query.filter(Cleaning.loc_id==loc_id).all()
        next_cleaning = return_next_cleaning(street_cleanings)
        place[2]= next_cleaning[1]
    #putting information in an organized dictionary
    results = {}
    for i in range (len(closest_places)):
        item = closest_places[i]
        message = "Try parking on %s. %s" %(item[3], item[2])
        results[str(i)] = {"km": item[0], "coordinates": item[1], "message": message, "num": i}
    return jsonify(results)


@app.route('/add_fave_loc')
def add_a_fave():
    street = request.args.get('street').replace("-", " ")
    address = int(request.args.get('address'))
    side = request.args.get('side')
    typefave = request.args.get ('type')
    if side == " " or side == None:
        location = find_location(address, street)
    else:
        location = find_location(address,street, side)
    add_fave_location(session['login'], location.loc_id, typefave, address)
    return redirect('/my_places')


@app.route('/my_places')
def my_places():
    if 'login' in session:
        home = FaveLocation.query.filter(FaveLocation.user_id==session['login'], FaveLocation.type_id=='hom').first()
        if home:
            home_location = Location.query.filter(Location.loc_id ==home.loc_id).first()
            street = Street.query.filter(Street.street_id == home_location.street_id).first()
            home_street = street.street_name
            home_address = home.address
            home_cleanings = Cleaning.query.filter(Cleaning.loc_id==home.loc_id).all()
            home_next_cleaning = return_next_cleaning(home_cleanings)[1]
            home = [home_address, home_street, home_next_cleaning]
        work = FaveLocation.query.filter(FaveLocation.user_id==session['login'], FaveLocation.type_id=='wor').first()
        if work:
            work_location = Location.query.filter(Location.loc_id == work.loc_id).first()
            street = Street.query.filter(Street.street_id == work_location.street_id).first()
            work_street = street.street_name
            work_address = work.address
            work_cleanings = Cleaning.query.filter(Cleaning.loc_id==work.loc_id).all()
            work_next_cleaning = return_next_cleaning(work_cleanings)[1]
            work = [work_address, work_street, work_next_cleaning]
        recent = FaveLocation.query.filter(FaveLocation.user_id==session['login'], FaveLocation.type_id=='las').first()
        if recent:
            recent_location = Location.query.filter(Location.loc_id==recent.loc_id).first()
            street = Street.query.filter(Street.street_id == recent_location.street_id).first()
            recent_street = street.street_name
            recent_address = recent.address
            recent_cleanings = Cleaning.query.filter(Cleaning.loc_id==recent.loc_id).all()
            recent_next_cleaning = return_next_cleaning(recent_cleanings)[1]
            recent = [recent_address, recent_street, recent_next_cleaning]

        streets = Street.query.order_by(Street.street_name.asc()).all()
        sides = Side.query.all()

        return render_template('/myplaces.html', 
                               recent=recent, 
                               work=work, 
                               home=home, 
                               streets=streets, 
                               sides=sides)
    else:
        flash("Please login to use")
        return redirect('/login')


# @app.route('/heatmap')
# def show_heat_map():
#     return render_template('map.html')

# @app.route('/get_all_locations.json')
# def get_all_locations():
#     print "1"
#     all_cleanings = Cleaning.query.all()
#     geos = []
#     for cleaning in all_cleanings:
#         print '2'
#         locations = Location.query.filter(Location.loc_id == cleaning.loc_id).all()
#         for location in locations:
#             print '3'
#             for geo in location.lng_lat:
#                 print '4'
#                 geos.append([float(geo[0]), float(geo[1])])
#     all_cleanings = {'all_geos': geos}
#     return jsonify(all_cleanings)

@app.route('/geo_for_map')
def get_geo_for_map():
    address = request.args.get("address")
    street = request.args.get("street").replace("-", " ")
    geo = find_geolocation(address, street)
    print geo
    return jsonify(geo)
  
if __name__ == "__main__":

    app.debug = True
    connect_to_db(app)


    app.run(port=5000, host='0.0.0.0')

