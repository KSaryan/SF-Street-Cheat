from sqlalchemy import func
from model import Location, Cleaning, Day, User, FaveLocation, Street, Side
#remove this when import app
from flask import Flask
from model import connect_to_db, db
import requests
# from server import app


def create_days():
    """Creates days in days tables"""

    print "Days"

    Day.query.delete()

    mon = Day(day_id="Mon", day_name="Monday")
    tue = Day(day_id="Tues", day_name="Tuesday")
    wed = Day(day_id="Wed", day_name="Wednesday")
    thu = Day(day_id="Thu", day_name="Thursday")
    fri = Day(day_id="Fri", day_name="Friday")
    sat = Day(day_id="Sat", day_name="Saturday")
    sun = Day(day_id="Sun", day_name="Sunday")
    hol = Day(day_id="Hol", day_name="Holiday")

    db.session.add_all([mon, tue, wed, thu, fri, sat, sun, hol])
    db.session.commit()


def create_cleanings():
    """Loads locations and cleanings from SODA API"""

    Location.query.delete()

    url = "https://data.sfgov.org/resource/u2ac-gv9v.json?$limit=39000&zip_code=94118"

    response = requests.get(url)
    if response.status_code == 200:
        print "Locations"
        data = response.json()

        for item in data:
            if Street.query.filter_by(street_name=item["streetname"]).first():
                s = Street.query.filter_by(street_name=item["streetname"]).first()
            else:
                s = Street(street_name=item["streetname"])
                db.session.add(s)
                db.session.commit()

            if Side.query.filter_by(side_name=item["blockside"]).first():
                side = Side.query.filter_by(side_name=item["blockside"]).first()
            else:
                side = Side(side_name=item["blockside"])
                db.session.add(side)
                db.session.commit()

            if Location.get_unique(s.street_id, item["rt_toadd"], item["lf_toadd"], side.side_id):
                
                location = Location(street_id=s.street_id, rt_from_address=item["rt_fadd"],
                                    rt_to_address=item["rt_toadd"], lt_from_address=item["lf_fadd"],
                                    lt_to_address=item["lf_toadd"], side_id=side.side_id)
                
                db.session.add(location)
                db.session.commit()

            else:
                location=db.session.query(Location).filter(Location.street_id==s.street_id, Location.rt_from_address==item["rt_fadd"],
                                    Location.rt_to_address==item["rt_toadd"], Location.lt_from_address==item["lf_fadd"],
                                    Location.lt_to_address==item["lf_toadd"], Location.side_id==side.side_id).first()

            day_id =item["weekday"]

            if day_id == "Holiday":
                day_id = "Hol"

            if item["week1ofmon"] == "Y":
                cleaning1 = Cleaning(day_id = day_id, start_time=item["fromhour"], end_time=item["tohour"], week_of_mon = 1, locations=location)
                db.session.add(cleaning1)
            if item["week2ofmon"] == "Y":
                cleaning2 = Cleaning(day_id = day_id, start_time=item["fromhour"], end_time=item["tohour"], week_of_mon = 2, locations=location)
                db.session.add(cleaning2)
            if item["week3ofmon"] == "Y":
                cleaning3 = Cleaning(day_id=day_id, start_time=item["fromhour"], end_time=item["tohour"], week_of_mon = 3, locations=location)
                db.session.add(cleaning3)
            if item["week4ofmon"] == "Y":
                cleaning4 = Cleaning(day_id=day_id, start_time=item["fromhour"], end_time=item["tohour"], week_of_mon = 4, locations=location)
                db.session.add(cleaning4)
            if item["week5ofmon"] == "Y":
                cleaning5 = Cleaning(day_id=day_id, start_time=item["fromhour"], end_time=item["tohour"], week_of_mon = 5, locations=location)
                db.session.add(cleaning5)

    db.session.commit()


# def create_user(email, password, phone=None):
#     """Creates new user"""

#     user=User(email=email, password=password, phone=phone)
#     db.session.add(user)
#     db.session.commit()


# def add_number(email, phone):
#     """updates user's phone number"""

#     user = db.session.query(User).filter_by(email=email).first()
#     user.phone=phone
#     #should I add here?
#     db.session.add(user)
#     db.session.commit()


def add_fave_location(user_id, loc_id):
    """adds new saved favorite location for user"""

    fave_location = FaveLocation(user_id=user_id, loc_id=loc_id)
    db.session.add(fave_location)
    db.session.commit()


if __name__ == "__main__":
    #later can import app from server
    app = Flask(__name__)
    connect_to_db(app)
    db.create_all()

    
    create_days()
    create_cleanings()


