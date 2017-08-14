from jinja2 import StrictUndefined
from flask import jsonify
from flask import (Flask, render_template, redirect, request, flash,
                   session, url_for, g)
# from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import update
from model import (Location, Cleaning, Day, User, Side, Type,
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
from functools import wraps
from place_class import Place



app = Flask(__name__)
app.secret_key = "ABC"



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.current_user is None:
            flash("Log in to access")
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def pre_process_all_requests():
    """Setup the request context"""

    user_id = session.get('user_id')
    if user_id:
        g.current_user = User.query.get(user_id)
        g.logged_in = True
        g.email = g.current_user.email
        g.user_id = g.current_user.user_id
        g.phone = g.current_user.phone
    else:
        g.logged_in = False
        g.current_user = None
        g.email = None


@app.route('/')
def homepage():
    """Displays homepage with login form"""
    if g.logged_in:
        return redirect ('/parking')
    return render_template('homepage.html')


@app.route('/logout')
def log_out():
    """Logs out user"""

    del session['user_id']

    return redirect ('/')


@app.route('/login')
def log_in():
    """Displays login page"""

    if g.logged_in:
        return redirect('/parking')
    return render_template('login.html')


@app.route('/verify_user', methods=["POST"])
def verify_user():
    """Verifies users email and password"""

    password = request.form.get("password")
    email = request.form.get("email")
    email = email.lower()
    q = db.session.query(User).filter(User.email==email).first()

    if not q:
        flash("Username or password not found")
        return redirect ('/')

  
    password = password.encode('utf8') 
    hashedpass = q.password.encode('utf8') 
    
    if bcrypt.checkpw(password, hashedpass):
        session['user_id'] = q.user_id
        return redirect('/parking')
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
        return redirect('/')
    elif len(phone) != 10:
        flash("Invalid number. Make sure to include area code.")
        return redirect('/')

    user = User(password=hashed, email=email, phone=phone)
    db.session.add(user)
    db.session.commit()
    session['user_id']= user.user_id
    return redirect('/parking')


@app.route('/user_info')
@login_required
def display_user_information():
    """Displays user information"""
    return render_template('user_info.html', user=g.current_user)


@app.route('/update_user', methods=["POST"])
def update_user_info():
    """Updates User Information"""

    email = request.form.get("email")
    password = request.form.get("password")
    number = request.form.get("number")
    user = User.query.get(g.user_id)
    if number:
        number=re.sub(r"[\-\(\)\.\s]+", "", number)

    if len(email) > 30:
        flash('Password or email too long')

    elif len(number) != 10:
        flash("Invalid number. Make sure to include area code.")

    else:
        email = email.lower()
        user.email = email.rstrip()
        password = password.rstrip()
        password = password.encode('utf8') 
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        user.password = hashed
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
    return render_template('parking.html', streets=streets, sides=sides)


@app.route('/street_cleaning.json')
def street_cleaning():
    """Returns time until street cleaning"""
    address = int(request.args.get("address"))
    street = Street.clean_street(request.args.get("street"))
    side = request.args.get("side")
    place = Place(address=address,
                  street=street,
                  side=side)
    
    geolocation = place.find_geolocation()

    now = get_datetime()
    
    towing_locs = place.get_towing_locs()
    towings = Towing.get_towings(towing_locs, now)
    towing_message = Towing.get_towing_message(towings)

    
    location = place.find_location()
    
    if location and g.logged_in:
        FaveLocation.add_fave_location(g.user_id, location.loc_id, 'las', address)

    result = prep_result(location, geolocation, towing_message)


    return jsonify(result)


@app.route('/current_location.json')
def get_current_location():
    """Use reverse geolocation to get nearest address"""

    lat = request.args.get("lat")
    lng = request.args.get("lng")
    url = "http://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&sensor=true"%(lat, lng)

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        street = (data["results"][0]["address_components"][1]["short_name"]).upper()
        address= re.sub(r'\-\d+', "", data["results"][0]["address_components"][0]["long_name"])
        place = Place(address=int(address), 
                      street=street)
        sides = place.get_sides_for_this_location()
        street = street.replace(" ", "-")
        address_info = {'street': street,
                        'address': address,
                        'sides': sides
                        }
    return jsonify(address_info)


@app.route('/find_sides.json')
def find_sides():
    """Returns sides of street associated with an address"""

    place = Place(address = int(request.args.get("address")),
                  street = Street.clean_street(request.args.get("street")))

    sides = place.get_sides_for_this_location()
    
    if sides:
        sides_json = {'sides': sides
                     }
        return jsonify(sides_json)
 
    return "no sides"


@app.route('/send_text.json', methods=["POST"])
@login_required
def send_text():
    """Creates a new message in the MessagesToSend table"""
    
    phone = g.current_user.phone

    if not phone:
        flash("You must have a phone number to get texts")
        result = {'info_message': 'False'}

        return jsonify(result)
  
    time = request.form.get("cleaningtime")
    message = MessageToSend(user_id=g.user_id, time=time)
    db.session.add(message)
    db.session.commit()
    result = {'info_message': 'True',
               'number': g.phone}

    return jsonify(result)



@app.route('/nearby_cleanings.json')
def find_nearby_cleanings():
    """returns nearby street cleanings with information needed for creating markers"""

    address = int(request.args.get("address"))
    street = Street.clean_street(request.args.get("street"))
    side = request.args.get("side")
    place = Place(street=street,
                  address=address,
                  side=side)
    closest_places = place.find_nearby_places()
    #replacing loc_id with message about when street cleaning is
    for place in closest_places:
        loc_id = place['loc_id']
        street_cleanings = Cleaning.query.filter(Cleaning.loc_id==loc_id).all()
        next_cleaning = get_next_cleaning(street_cleanings)
        place['message']= next_cleaning['message']
    #putting information in an organized dictionary
    results = {}
    for i in range (len(closest_places)):
        item = closest_places[i]
        message = "Try parking on %s. %s" %(item['street'], item['message'])
        results[str(i)] = {"km": item['km'], "coordinates": item['lat-lng'], "message": message, "num": i}
    return jsonify(results)


@app.route('/add_fave_loc')
def add_a_fave():
    """Adds a new location to FaveLocation table"""
    
    street = Street.clean_street(request.args.get("street"))
    address = int(request.args.get('address'))
    side = request.args.get('side')

    place = Place(street=street,
                  address=address,
                  side=side)

    typefave = request.args.get('type')
   
    location = place.find_location()

    FaveLocation.add_fave_location(g.user_id, location.loc_id, typefave, address)
    return redirect('/my_places')


@app.route('/my_places')
@login_required
def my_places():
    """Displays users saved places"""

    all_places =[]
    places = db.session.query(FaveLocation).filter(FaveLocation.user_id==g.user_id).all()
    for place in places:
        typed = place.typed.type_name
        place_location = Location.query.filter(Location.loc_id ==place.loc_id).first()
        street = Street.query.filter(Street.street_id == place_location.street_id).first()
        place_street = street.street_name
        place_address = place.address
        place_cleanings = Cleaning.query.filter(Cleaning.loc_id==place.loc_id).all()
        place_next_cleaning = get_next_cleaning(place_cleanings)['message']
        place = [place_address, place_street, place_next_cleaning, typed]
        all_places.append(place)

    fave_places = db.session.query(Type).all()
    streets = Street.query.order_by(Street.street_name.asc()).all()
    sides = Side.query.all()

    return render_template('/myplaces.html', 
                           all_places=all_places, 
                           streets=streets, 
                           sides=sides,
                           fave_places=fave_places)


#for heatmap I decided not to use

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

# @app.route('/geo_for_map')
# def get_geo_for_map():
#     place = Place(address = request.args.get("address"), 
#                   street= Street.clean_street(request.args.get("street")))
#     geo = place.find_geolocation()
#     return jsonify(geo)
  
if __name__ == "__main__":

    app.debug = True
    connect_to_db(app)


    app.run(port=5000, host='0.0.0.0')

