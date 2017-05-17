from jinja2 import StrictUndefined
from flask import jsonify
from flask import (Flask, render_template, redirect, request, flash,
                   session, url_for)
# from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import update
from model import (Location, Cleaning, Day, User, Side, 
                   Street, FaveLocation, MessageToSend, connect_to_db, db)
import json
from datetime import datetime, timedelta, date
import bcrypt
import pytz
import requests
import re

import os
from helpers import *
import math
from operator import itemgetter



app = Flask(__name__)
app.secret_key = "ABC"

@app.route('/')
def homepage():
    """Displays homepage with login form"""

    if 'login' in session:
        return redirect('/parking')
    else:
        return render_template('homepage.html')


@app.route('/', methods=["POST"])
def log_out():
    """logs out user"""

    del session['login']
    flash('Successfully loged out')

    return redirect ('/')


@app.route('/verify_user', methods=["POST"])
def verify_user():
    """Verifies users email and password"""

    password = request.form.get("password")
    email = request.form.get("email")
    email = email.lower()

    q = db.session.query(User).filter(User.email==email, User.password==password).first()

    if q:
        session['login'] = q.user_id
        return redirect('/parking')
    else:
        flash("Username or password not found")
        return redirect ('/')


@app.route('/create_user', methods=["POST"])
def create_user():
    """Creates new user in database"""

    password = request.form.get("password")
    #not working
    # hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    email = request.form.get("email")
    email = email.lower()

    q = db.session.query(User).filter(User.email==email).first()
    if q:
        flash('There is already an email associated with this account. Please login.')
        return redirect('/')
    else:
        user = User(password=password, email=email)
        db.session.add(user)
        db.session.commit()
        session['login']= user.user_id
        flash('Thank you for creating an account')
        return redirect('/parking')


@app.route('/user_info')
def display_user_information():
    """displays user information"""

    if 'login' in session:
        user = User.query.get(session['login'])
        return render_template('user_info.html', user=user)
    else:
        flash("Please login in to view")
        return redirect ('/')


@app.route('/update_user', methods=["POST"])
def update_user_info():
    """Updates User Information"""

    email=request.form.get("email")
    password=request.form.get("password")
    number=request.form.get("number")
    user=User.query.get(session['login'])
    if email:
        email=email.lower()
        user.email=email
        user.password=password
    
    if number:
        number=number.replace("-", "")
        number=number.replace(" ", "")
        number=number.replace("(", "")
        number=number.replace(")", "")
        user.phone=number
    
    db.session.add(user)
    db.session.commit()

    flash('Information Updated')
    return redirect('/user_info')


@app.route('/parking')
def parking():
    """Allows user to submit new parking information"""

    streets = Street.query.order_by(Street.street_name.asc()).all()
    sides = Side.query.all()
    if 'login' in session:
        return render_template('parking.html', streets=streets, sides=sides)
    else:
        flash("Please login")
        return redirect('/')


@app.route('/street_cleaning.json')
def street_cleaning():
    """Returns time until street cleaning"""

    number = int(request.args.get("address"))
    street = (request.args.get("street")).replace("-", " ")
    side = request.args.get("side")
    location = find_location(number, street, side)
    if location:
        faveloc = FaveLocation(user_id = session['login'], loc_id = location.loc_id)
        street_cleanings = Cleaning.query.filter(Cleaning.loc_id==location.loc_id).all()

        next_cleaning = find_next_cleaning(street_cleanings)
        if next_cleaning[0] == "now":
            result = {"info_message": next_cleaning[0], 
                      "message": next_cleaning[1]}

        else:
            result = {"info_message": next_cleaning[0], 
                      "message": next_cleaning[1],
                      "cleaning_time":next_cleaning[2]}
    else:
        message = "Not a valid address"
        result = {"info_messge": "not a valid address",
                  "message": message}


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
    sides_json = {'sides': sides
                 }
    return jsonify(sides_json)


@app.route('/send_text', methods=["POST"])
def send_text():
    """Creates a new message in the MessagesToSend table"""

    user = User.query.get(session["login"])
    if user.phone:
        time = request.form.get("cleaningtime")
        message = MessageToSend(user_id=session['login'], time= time)
        db.session.add(message)
        db.session.commit()
        return "True"
    else:
        flash("You must have a phone number to get texts")
        return "False"

@app.route('/nearby_cleanings')
def find_nearby_cleanings():
    address = int(request.args.get("address"))
    street = (request.args.get("street")).replace("-", " ")
    side = request.args.get("side")
    # current_location = find_location(address, street, side)
    street = street.split(" ")
    address = str(address)
    address_string = street[0] + "+" + street[1] + "+" + address + "+San+Francisco+CA"
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=AIzaSyB0OiwKI95QDFdX-GkLuGipWuYuf-RyEcQ"%(address_string)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        geolocation = data["results"][0]["geometry"]["location"]
    locations = Location.query.all()
    overall_distances = []
    for location in locations:
        distances = []
        for coordinate in location.lng_lat:
            distance = math.sqrt((coordinate[1]-geolocation['lat'])**2 + (coordinate[0]-geolocation['lng'])**2)
            distances.append([distance, coordinate])
        distances = sorted(distances, key=itemgetter(0))
        best_distance = distances[-1]
        overall_distances.append(best_distance)
    overall_distances = sorted(overall_distances, key=itemgetter(0))
    closest_places = overall_distances[-5:]
    return jsonify(closest_places)


  
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)


    app.run(port=5000, host='0.0.0.0')

