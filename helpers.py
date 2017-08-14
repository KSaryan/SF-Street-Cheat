from model import (Location, Cleaning, Day, User, Side, 
                   Street, FaveLocation, MessageToSend, 
                   Towing, Tow_Location, Tow_Side, connect_to_db, db)
from datetime import datetime, timedelta
import pytz
import requests
from math import radians, cos, sin, asin, sqrt
from operator import itemgetter


def get_datetime():
  """Returns current datetime"""

  pacific = pytz.timezone('US/Pacific')
  return datetime.now(tz=pacific)


def find_next_cleaning(street_cleanings, now):
  """Finds a cleaning on an upcoming day"""

  while True:
        now = now + timedelta(days=1)
        day = now.strftime("%a")
        date = int(now.strftime("%d"))
        week_of_mon = (date / 7) + 1
        for cleaning in street_cleanings:
            if cleaning.week_of_mon == week_of_mon and cleaning.day_id == day:
                current_time = get_datetime()
                days = now - current_time
                days = days.days
                month = now.strftime("%B")
                date = now.strftime("%d")
                message =  "Next cleaning is in %s days. On %s, %s %s. From %s to %s (military time)." %(days, 
                                                                                                         cleaning.day.day_name, 
                                                                                                         month, 
                                                                                                         date, 
                                                                                                         cleaning.start_time, 
                                                                                                         cleaning.end_time)
                message = message.replace("in 0 days", "tomorrow")
                today = get_datetime()
                year = str(today.year)
                cleaning_time_string = month + "-" + date + "-" + year +" " + cleaning.start_time
                cleaning_time = datetime.strptime(cleaning_time_string, '%B-%d-%Y %H:%M')
                return {'info':"another day", 'message': message, 'cleaning_time': cleaning_time}


def find_todays_cleaning(street_cleanings, now):
  """Finds a cleaning on the same day"""

  day = now.strftime("%a")
  date = int(now.strftime("%d"))
  week_of_mon = (date / 7) + 1

  for cleaning in street_cleanings:
        if cleaning.week_of_mon == week_of_mon and cleaning.day_id == day:
            start_time = datetime.strptime(cleaning.start_time, '%H:%M')
            end_time = datetime.strptime(cleaning.end_time, '%H:%M')
            if int(end_time.strftime("%H")) > int(now.strftime("%H")):
                if int(start_time.strftime("%H")) >= int(now.strftime("%H")):
                    hours = int(start_time.strftime("%H")) - int(now.strftime("%H"))
                    cleaning_time = get_datetime() + timedelta(hours=hours)
                    message = "Street cleaning is today. It's in %s hours." %(str(hours))
                    return {'info':"today", 'message':message, 'cleaning_time':cleaning_time}
                elif int(start_time.strftime("%H")) <= int(now.strftime("%H")):
                    return {'info': "now", 'message': "Street cleaning is now"}
  return False


def get_next_cleaning(street_cleanings):
    """Returns date of next cleaning"""
    
    now = get_datetime()

    if find_todays_cleaning(street_cleanings, now):
      return find_todays_cleaning(street_cleanings, now)

    else:
      return find_next_cleaning(street_cleanings, now)


def prep_result(location, geolocation, towing_message):
  if location:
    street_cleanings = Cleaning.query.filter(Cleaning.loc_id==location.loc_id).all()

    next_cleaning = get_next_cleaning(street_cleanings)

    holiday = location.check_for_holidays()

    if next_cleaning['info'] == "now":
        result = {"info_message": next_cleaning['info'], 
                  "message": next_cleaning['message'] + "/n" + holiday,
                  "geolocation": geolocation,
                  "towing": towing_message}

    else:
        result = {"info_message": next_cleaning['info'], 
                  "message": next_cleaning['message'] + "\n" + holiday,
                  "cleaning_time":next_cleaning['cleaning_time'],
                  "geolocation": geolocation,
                  "towing": towing_message}
  else:
    message = "Not a valid address or no street cleaning in area (Russian Hill)"
    result = {"info_messge": "not a valid address",
              "message": message,
              "geolocation": geolocation}

  return result


