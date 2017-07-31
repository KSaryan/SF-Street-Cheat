from sqlalchemy import func
from model import (Location, Cleaning, Day, User, 
                   FaveLocation, Street, Side, Neighborhood, 
                   Type, Towing, Tow_Location, Tow_Side)
from flask import Flask
from model import connect_to_db, db
import requests


def create_days():
    """Creates days in days tables"""

    print "Days"

    Day.query.delete()

    mon = Day(day_id="Mon", day_short="Mo", day_name="Monday")
    tue = Day(day_id="Tue", day_short="Tu", day_name="Tuesday")
    wed = Day(day_id="Wed", day_short="We", day_name="Wednesday")
    thu = Day(day_id="Thu", day_short="Th", day_name="Thursday")
    fri = Day(day_id="Fri", day_short="Fr", day_name="Friday")
    sat = Day(day_id="Sat", day_short="Sa", day_name="Saturday")
    sun = Day(day_id="Sun", day_short="Su", day_name="Sunday")
    hol = Day(day_id="Hol", day_short="Ho", day_name="Holiday")

    db.session.add_all([mon, tue, wed, thu, fri, sat, sun, hol])
    db.session.commit()


def create_types():
    """creates types in the types table"""

    print "Types"

    Type.query.delete()

    hom = Type(type_id="hom", type_name="home")
    wor = Type(type_id="wor", type_name="work")
    las = Type(type_id="las", type_name="last")

    db.session.add_all([hom, wor, las])
    db.session.commit()


def create_cleanings():
    """Loads locations and cleanings from SODA API"""

    Location.query.delete()

    url = "https://data.sfgov.org/resource/u2ac-gv9v.json?$limit=39000"

    response = requests.get(url)
    if response.status_code == 200:
        print "Locations"
        data = response.json()

        for item in data:
            #add street to streets table
            s = Street.query.filter_by(street_name=item["streetname"]).first()
            if s is None:
                s = Street(street_name=item["streetname"])
                db.session.add(s)
                db.session.commit()

            # add neighborhood to neighborhoods table
            n = Neighborhood.query.filter_by(n_name=item["nhood"]).first()
            if n is None:
                n = Neighborhood(n_name=item["nhood"])
                db.session.add(n)
                db.session.commit()

            #add side to sides table
            if "blockside" in item:
                side = Side.query.filter_by(side_name=item["blockside"]).first()  
                if side is None:
                    side = Side(side_name=item["blockside"])
                    db.session.add(side)
                    db.session.commit()
                side_id = side.side_id
            else:
                side_id = None

            #add location to locations table
            location=db.session.query(Location).filter(Location.street_id==s.street_id, Location.rt_from_address==item["rt_fadd"],
                                    Location.rt_to_address==item["rt_toadd"], Location.lt_from_address==item["lf_fadd"],
                                    Location.lt_to_address==item["lf_toadd"], Location.side_id==side_id).first()
            if location is None:
                location = Location(street_id=s.street_id, n_id=n.n_id, rt_from_address=item["rt_fadd"],
                                    rt_to_address=item["rt_toadd"], lt_from_address=item["lf_fadd"],
                                    lt_to_address=item["lf_toadd"], side_id=side_id,
                                    lng_lat = item["geometry"]["coordinates"])
                db.session.add(location)
                db.session.commit()
                

            day_id =item["weekday"]

            if day_id == "Holiday":
                day_id = "Hol"

            if day_id == "Tues":
                day_id = "Tue"

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


def create_tow_sides():
    """adds sides to tow_sides table"""

    print "Tow Sides"

    Tow_Side.query.delete()

    lef = Tow_Side(tow_side_name="Left")
    rig = Tow_Side(tow_side_name="Right")

    db.session.add_all([lef, rig])
    db.session.commit()


def create_towings():
    """loads towings locations and towings from SODA API"""

    Tow_Location.query.delete()
    Towing.query.delete()


    url = "https://data.sfgov.org/resource/wnhf-gu86.json"

    response = requests.get(url)
    if response.status_code == 200:
        print "Towings"
        data = response.json()

        for item in data:
            if item["street"] == "HARRISON":
                street_name = item["street"] + " ST"
            elif "st_type" in item:
                street_name = item["street"] + " " + item["st_type"]
            else:
                street_name = item["street"]
            street = Street.query.filter_by(street_name=street_name).first()
            street_id = street.street_id

            tow_side = Tow_Side.query.filter_by(tow_side_name=item["side"]).first()
            tow_side_id = tow_side.tow_side_id

            if item['lf_fadd'] == '0.0':
                lf_fadd = 0
            else:
                lf_fadd = int(item["lf_fadd"].rstrip(".0"))
            if item['lf_toadd'] == '0.0':
                lf_toadd = 0
            else:
                lf_toadd = int(item["lf_toadd"].rstrip(".0"))
            if item['rt_toadd'] == '0.0':
                rt_toadd = 0
            else:
                rt_toadd = int(item["rt_toadd"].rstrip(".0"))
            if item['rt_fadd'] == '0.0':
                rt_fadd = 0
            else:
                rt_fadd = int(item["rt_fadd"].rstrip(".0"))


            location=Tow_Location.query.filter(Tow_Location.street_id==street_id, Tow_Location.rt_from_address==rt_fadd,
                                               Tow_Location.rt_to_address==rt_toadd, Tow_Location.lt_from_address==lf_fadd,
                                               Tow_Location.lt_to_address==lf_toadd, Tow_Location.tow_side_id==tow_side_id).first()
            if location is None:
                location = Tow_Location(street_id=street_id, rt_from_address=rt_fadd,
                                        rt_to_address=rt_toadd, lt_from_address=lf_fadd,
                                        lt_to_address=lf_toadd, tow_side_id=tow_side_id)
                db.session.add(location)
                db.session.commit()
                

            days = item["tow1days"].split(",")

            for day in days:
                day = Day.query.filter_by(day_short=day).first()
                day_id = day.day_id

                towing = Towing(tow_loc_id=location.tow_loc_id, start_time=item["towperiod"], day_id=day_id)

                db.session.add(towing)
                db.session.commit()


if __name__ == "__main__":
    app = Flask(__name__)
    connect_to_db(app)
    db.create_all()

    
    create_days()
    create_types()
    create_cleanings()
    create_tow_sides()
    create_towings()
    


