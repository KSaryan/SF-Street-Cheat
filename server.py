from jinja2 import StrictUndefined
from flask import jsonify
from flask import (Flask, render_template, redirect, request, flash,
                   session, url_for)
# from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import update
from model import (Location, Cleaning, Day, User, Side, 
                   Street, FaveLocation, connect_to_db, db, find_next_cleaning)
import json
from datetime import datetime, timedelta, date
import bcrypt
import pytz
import requests

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
        user = User(password=hashed, email=email)
        db.session.add(user)
        db.session.commit()
        session['login']= user.user_id
        flash('Thank you for creating an account')
        return redirect('/parking')


@app.route('/user_info')
def display_user_information():
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


@app.route('/street_cleaning')
def street_cleaning():
    """Returns time until street cleaning"""

    number = int(request.args.get("address"))
    street = (request.args.get("street")).replace("-", " ")
    side = request.args.get("side")
    street1 = Street.query.filter(Street.street_name == street).first()
    side1 = Side.query.filter(Side.side_name==side).first()
    if number % 2 == 0:
        location = Location.query.filter(Location.side_id==side1.side_id,
                                          Location.street_id==street1.street_id,
                                          Location.rt_from_address <= number, 
                                          Location.rt_to_address >= number).first()
    else: 
        location = Location.query.filter(Location.side_id==side1.side_id,
                                          Location.street_id==street1.street_id,
                                          Location.lt_from_address <= number, 
                                          Location.lt_to_address >= number).first()
    if location:
        street_cleanings = Cleaning.query.filter(Cleaning.loc_id==location.loc_id).all()

        next_cleaning = find_next_cleaning(street_cleanings)
        pacific = pytz.timezone('US/Pacific')
        if next_cleaning == "Street cleaning is now":
            message1 = next_cleaning
            return message1
        elif next_cleaning[0] == "later today":
            hours = next_cleaning[1]
            return " Street cleaning is today. It's in %s hours." %(hours)
        else:
            days = int(next_cleaning[0].strftime('%d')) - int(datetime.now(tz=pacific).strftime('%d'))

            cleaning = next_cleaning[1]

            month = next_cleaning[0].strftime("%B")

            date = next_cleaning[0].strftime("%d")

            return  "Next cleaning is in %s days. On %s, %s %s. From %s to %s." %(days, 
                                                                                  cleaning.days.day_name, 
                                                                                  month, 
                                                                                  date, 
                                                                                  cleaning.start_time, 
                                                                                  cleaning.end_time)
    else:
        return "Not a valid address"

@app.route('/current_location')
def get_current_location():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    print lat 
    print lng
    url = "http://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&sensor=true"%(lat, lng)

    response = requests.get(url)
    print response
    if response.status_code == 200:
        data = response.json()
        address = data["results"][0]["address_components"][1]["long_name"]
    return address


# @app.route('/side_decider')
# def side_decider():
#     sides = []
#     number = int(request.args.get("address"))
#     street = (request.args.get("street")).replace("-", " ")
#     street1 = Street.query.filter(Street.street_name == street).first()
#     if number % 2 == 0:
#         locations = Location.query.filter(Location.street_id==street1.street_id,
#                                           Location.rt_from_address <= number, 
#                                           Location.rt_to_address >= number).all()
#     else: 
#         locations = Location.query.filter(Location.street_id==street1.street_id,
#                                           Location.lt_from_address <= number, 
#                                           Location.lt_to_address >= number).all()
#     for location in locations:
#         if location.side_id: 
#             sides.append(location.sides.side_name)

#     return sides

  
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)


    app.run(port=5000, host='0.0.0.0')

