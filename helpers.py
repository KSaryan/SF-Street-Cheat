from model import (Location, Cleaning, Day, User, Side, 
                   Street, FaveLocation, MessageToSend, 
                   Towing, Tow_Location, Tow_Side, connect_to_db, db)
from datetime import datetime, timedelta
import pytz
import requests
from math import radians, cos, sin, asin, sqrt
from operator import itemgetter

def get_datetime():
  """returns current datetime"""

  pacific = pytz.timezone('US/Pacific')
  return datetime.now(tz=pacific)


def check_for_holidays(street_cleanings):
  for cleaning in street_cleanings:
    if cleaning.day_id == 'Hol':
      return "There are holiday hours associated with this location. They are %s - %s (military time.)" %(cleaning.start_time, cleaning.end_time)

  return None


def get_towing_locs(address, street):
  """finds towing_locations for address"""

  street1 = Street.query.filter(Street.street_name == street).first()
  tow_locs = Tow_Location.query.filter()
  address = int(address)
  if address % 2 == 0:
      locations = Tow_Location.query.filter(Tow_Location.street_id==street1.street_id,
                                        Tow_Location.rt_from_address <= address, 
                                        Tow_Location.rt_to_address >= address).all()
  else: 
      locations = Tow_Location.query.filter(Tow_Location.street_id==street1.street_id,
                                        Tow_Location.lt_from_address <= address, 
                                        Tow_Location.lt_to_address >= address).options(db.joinedload('towings')).all()

  return locations


def get_towings(towing_locs):
  """finds next two towing times"""

  now = get_datetime()
  day = now.strftime("%a")
  tomorrow = now + timedelta(days=1)
  tomorrow_day = tomorrow.strftime("%a")

  towings_list = []
  for loc in towing_locs:
    # loc_id = loc.tow_loc_id
    # towings = Towing.query.filter(Towing.tow_loc_id==loc_id).all()
    towings_list.extend(loc.towings)
  # print towings_list
  next_towings = []
  for towing in towings_list:
    if towing.day_id == day or towing.day_id == tomorrow_day:
      next_towings.append(towing)
  return next_towings [:2]


def get_towing_message(towings):
  """creates message about towing"""

  t_mesages = []
  if towings:
      for t in towings:
          t_side = t.tow_location.tow_side.tow_side_name
          t_side = (t_side.rstrip(" Sides")).lower()
          t_message = "There is towing on the %s side(s) of this street on %s, at %s."%(t_side, t.day.day_name, t.start_time)
          t_mesages.append(t_message)
  towing_message = ""
  for message in t_mesages:
      towing_message += message
  return towing_message


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
                return ["another day", message, cleaning_time]


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
                    return ["today", message, cleaning_time]
                elif int(start_time.strftime("%H")) <= int(now.strftime("%H")):
                    return ["now", "Street cleaning is now"]
  return False


def return_next_cleaning(street_cleanings):
    """Returns date of next cleaning"""
    
    now = get_datetime()

    if find_todays_cleaning(street_cleanings, now):
      return find_todays_cleaning(street_cleanings, now)

    else:
      return find_next_cleaning(street_cleanings, now)
        

def get_sides_for_this_location(street, address):
    """returns sides of street associated with unique location"""
    street1 = Street.query.filter_by(street_name = street).first()
    if int(address) % 2 == 0:
        locations = Location.query.filter(Location.street_id==street1.street_id,
                                          Location.rt_from_address <= address, 
                                          Location.rt_to_address >= address).options(db.joinedload('side')).all()
    else: 
        locations = Location.query.filter(Location.street_id==street1.street_id,
                                          Location.lt_from_address <= address, 
                                          Location.lt_to_address >= address).options(db.joinedload('side')).all()
    sides = []
    for loc in  locations:
      if loc.side:
        sides.append(loc.side.side_name)
    return sides


def find_location(number, street, side = None):
    """returns unique location from locations table"""

    street1 = Street.query.filter(Street.street_name == street).first()

    if side:
      side1 = Side.query.filter(Side.side_name==side).first()
      side_id = side1.side_id
    else:
      side_id =None

    if number % 2 == 0:
        location = Location.query.filter(Location.side_id==side_id,
                                          Location.street_id==street1.street_id,
                                          Location.rt_from_address <= number, 
                                          Location.rt_to_address >= number).first()
    else: 
        location = Location.query.filter(Location.side_id==side_id,
                                          Location.street_id==street1.street_id,
                                          Location.lt_from_address <= number, 
                                          Location.lt_to_address >= number).first()

    return location


def find_geolocation(address, street):
  """returns geolocation of address and street"""

  street = street.split(" ")
  address = str(address)
  address_string = street[0] + "+" + street[1] + "+" + address + "+San+Francisco+CA"
  url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=AIzaSyB0OiwKI95QDFdX-GkLuGipWuYuf-RyEcQ"%(address_string)
  response = requests.get(url)
  if response.status_code == 200:
      data = response.json()
      return data["results"][0]["geometry"]["location"]


def find_nearby_places(address, street, side):
  """returns list of closest street cleaning routes 


  as tuple of distance, coordinate, and loc_id"""
  
  current_location = find_location(address, street, side)
  geolocation = find_geolocation(address, street)
  locations = Location.query.filter(Location.loc_id != current_location.loc_id, 
                                    Location.n_id == current_location.n_id).all()
  overall_distances = []
  for location in locations:
      distances = []
      for coordinate in location.lng_lat:
          coordinate = [float(coordinate[0]), float(coordinate[1])]
          lon1, lat1, lon2, lat2 = map(radians, [coordinate[0], coordinate[1], geolocation['lng'], geolocation['lat']])
          dlon = lon2 - lon1 
          dlat = lat2 - lat1 
          a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
          c = 2 * asin(sqrt(a)) 
          km = 6367 * c
# stance = math.sqrt((-Decimal())**2 + (-Decimal())**2)
          distances.append([km, coordinate, location.loc_id, location.street.street_name])
      distances = sorted(distances, key=itemgetter(0))
      best_distance = distances[1]
      overall_distances.append(best_distance)
  overall_distances = sorted(overall_distances, key=itemgetter(0))
  closest_places = overall_distances[:25]
  return closest_places


def add_fave_location(user_id, loc_id, type_id, address):
  """adds new saved favorite location for user or updates existing"""
  
  fl = FaveLocation.query.filter(FaveLocation.user_id==user_id, FaveLocation.type_id==type_id).first()
  if fl:
    fl.loc_id = loc_id
    fl.address = address
  else:
    fl = FaveLocation(user_id=user_id, loc_id=loc_id, type_id=type_id, address=address)
  
  db.session.add(fl)
  db.session.commit()


