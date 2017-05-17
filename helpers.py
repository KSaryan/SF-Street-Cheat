from model import (Location, Cleaning, Day, User, Side, 
                   Street, FaveLocation, MessageToSend, connect_to_db, db)
from datetime import datetime, timedelta
import pytz

def find_next_cleaning(street_cleanings):
    """Returns date of next cleaning"""

    pacific = pytz.timezone('US/Pacific')
    now = datetime.now(tz=pacific)
    day = now.strftime("%a")
    if day == "Thu":
        day = "Thur"
    date = int(now.strftime("%d"))
    week_of_mon = (date / 7) + 1

    for cleaning in street_cleanings:
        if cleaning.week_of_mon == week_of_mon and cleaning.day_id == day:
            start_time = datetime.strptime(cleaning.start_time, '%H:%M')
            end_time = datetime.strptime(cleaning.end_time, '%H:%M')
            if int(end_time.strftime("%H")) > int(now.strftime("%H")):
                if int(start_time.strftime("%H")) > int(now.strftime("%H")):
                    hours = int(start_time.strftime("%H")) - int(now.strftime("%H"))
                    cleaning_time = datetime.now() + timedelta(hours=hours)
                    message = " Street cleaning is today. It's in %s hours." %(str(hours))
                    return ["today", message, cleaning_time]
                elif int(end_time.strftime("%H")) < int(now.strftime("%H")):
                    return ["now", "Street cleaning is now"]
        
    while True:
        now = now + timedelta(days=1)
        day = now.strftime("%a")
        if day == "Thu":
            day = "Thur"
        if day == "Tue":
            day = "Tues"
        date = int(now.strftime("%d"))
        week_of_mon = (date / 7) + 1
        for cleaning in street_cleanings:
            if cleaning.week_of_mon == week_of_mon and cleaning.day_id == day:
                days = int(now.strftime('%d')) - int(datetime.now(tz=pacific).strftime('%d'))
                month = now.strftime("%B")
                date = now.strftime("%d")
                message =  "Next cleaning is in %s days. On %s, %s %s. From %s to %s (military time)." %(days, 
                                                                                                         cleaning.days.day_name, 
                                                                                                         month, 
                                                                                                         date, 
                                                                                                         cleaning.start_time, 
                                                                                                         cleaning.end_time)
                today = datetime.now(tz=pacific)
                year = str(today.year)
                cleaning_time_string = month + "-" + date + "-" + year +" " + cleaning.start_time
                cleaning_time = datetime.strptime(cleaning_time_string, '%B-%d-%Y %H:%M')
                return ["another day", message, cleaning_time]


def get_sides_for_this_location(street, address):
    street1 = Street.query.filter_by(street_name = street).first()
    if int(address) % 2 == 0:
        locations = Location.query.filter(Location.street_id==street1.street_id,
                                          Location.rt_from_address <= address, 
                                          Location.rt_to_address >= address).all()
    else: 
        locations = Location.query.filter(Location.street_id==street1.street_id,
                                          Location.lt_from_address <= address, 
                                          Location.lt_to_address >= address).all()
    sides = []
    for location in locations:
        sides.append(location.sides.side_name)
    return sides

def find_location(number, street, side):
    import pdb; pdb.set_trace()
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
    return location