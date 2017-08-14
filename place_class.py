import requests 
from model import *
from math import radians, cos, sin, asin, sqrt
from operator import itemgetter

class Place(object):

	def __init__(self, address, street, side=None):
		self.address = address
		self.street =street
		self.side = side 


	def __repr__(self):
		return '<address: {}, street: {}>'.format(self.address, self.street)

	def find_geolocation(self):
		"""returns geolocation of address and street"""

		street = self.street.split(" ")
		address = str(self.address)
		address_string = street[0] + "+" + street[1] + "+" + address + "+San+Francisco+CA"
		url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=AIzaSyB0OiwKI95QDFdX-GkLuGipWuYuf-RyEcQ"%(address_string)
		response = requests.get(url)
		if response.status_code == 200:
		  data = response.json()
		  return data["results"][0]["geometry"]["location"]

	def find_location(self):
	    """returns unique location from locations table"""

	    street1 = Street.query.filter(Street.street_name == self.street).first()
	    try:
	      side_id = Side.query.filter(Side.side_name==self.side).first().side_id
	    except:
	      side_id = None

	    if self.address % 2 == 0:
	        location = Location.query.filter(Location.side_id==side_id,
	                                          Location.street_id==street1.street_id,
	                                          Location.rt_from_address <= self.address, 
	                                          Location.rt_to_address >= self.address).first()
	    else: 
	        location = Location.query.filter(Location.side_id==side_id,
	                                          Location.street_id==street1.street_id,
	                                          Location.lt_from_address <= self.address, 
	                                          Location.lt_to_address >= self.address).first()

	    return location

	def get_sides_for_this_location(self):
	    """returns sides of street associated with unique location"""

	    street1 = Street.query.filter_by(street_name = self.street).first()
	    if self.address % 2 == 0:
	        locations = Location.query.filter(Location.street_id==street1.street_id,
	                                          Location.rt_from_address <= self.address, 
	                                          Location.rt_to_address >= self.address).options(db.joinedload('side')).all()
	    else: 
	        locations = Location.query.filter(Location.street_id==street1.street_id,
	                                          Location.lt_from_address <= self.address, 
	                                          Location.lt_to_address >= self.address).options(db.joinedload('side')).all()
	    sides = []
	    for loc in  locations:
	      if loc.side:
	        sides.append(loc.side.side_name)
	    return sides

	def find_nearby_places(self):
	  """returns list of closest street cleaning routes"""
	  
	  current_location = self.find_location()
	  geolocation = self.find_geolocation()
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
	# distance = math.sqrt((-Decimal())**2 + (-Decimal())**2)
	          distances.append([km, coordinate, location.loc_id, location.street.street_name])
	      distances = sorted(distances, key=itemgetter(0))
	      best_distance = distances[1]
	      overall_distances.append(best_distance)
	  overall_distances = sorted(overall_distances, key=itemgetter(0))
	  closest_places = overall_distances[:25]
	  closest_places = [{'km': x[0], 'lat-lng': x[1], 'loc_id': x[2], 'street': x[3]} for x in closest_places]
	  return closest_places

	def get_towing_locs(self):
		"""finds towing_locations for address"""

		street1 = Street.query.filter(Street.street_name == self.street).first()
		tow_locs = Tow_Location.query.filter()
		if self.address % 2 == 0:
		  	locations = Tow_Location.query.filter(Tow_Location.street_id==street1.street_id,
		                                    	  Tow_Location.rt_from_address <= self.address, 
		                                    	  Tow_Location.rt_to_address >= self.address).all()
		else: 
		  locations = Tow_Location.query.filter(Tow_Location.street_id==street1.street_id,
		                                    Tow_Location.lt_from_address <= self.address, 
		                                    Tow_Location.lt_to_address >= self.address).options(db.joinedload('towings')).all()

		return locations