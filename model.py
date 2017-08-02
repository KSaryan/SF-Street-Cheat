from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
import pytz
import bcrypt

db = SQLAlchemy()

class Street(db.Model):
    """Streets in SF"""

    __tablename__ = "streets"

    street_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    street_name = db.Column(db.String(20), nullable=False)

    def __repr__ (self):
        """Displayed when called"""

        return "<%s>"%(self.street_name)


class Side(db.Model):
    """Street Sides"""

    __tablename__ = "sides"

    side_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    side_name = db.Column(db.String(10), nullable=False)

    def __repr__ (self):
        """Displayed when called"""

        return "<%s>"%(self.side_name)


class Neighborhood(db.Model):
    """Neighborhoods"""

    __tablename__ = "neighborhoods"

    n_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    n_name = db.Column(db.String(25), nullable=False)

    def __repr__ (self):
        """Displayed when called"""

        return "<%s>"%(self.n_name)


class Location(db.Model):
    """Specific address."""

    __tablename__ = "locations"

    loc_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    street_id = db.Column(db.Integer, db.ForeignKey('streets.street_id'))
    n_id = db.Column(db.Integer, db.ForeignKey('neighborhoods.n_id'))
    rt_from_address = db.Column(db.Integer, nullable=False)
    rt_to_address = db.Column(db.Integer, nullable=False)
    lt_from_address = db.Column(db.Integer, nullable=False)
    lt_to_address = db.Column(db.Integer, nullable=False)
    side_id = db.Column(db.Integer, db.ForeignKey('sides.side_id'))
    lng_lat = db.Column(db.ARRAY(db.Numeric, dimensions=2), nullable=False)
    
    side = db.relationship('Side', backref='locations')
    street = db.relationship('Street', backref='locations')
    neighborhood = db.relationship('Neighborhood', backref='locations')

    def __repr__ (self):
        """Displayed when called"""

        return "<rt: %s-%s, lt: %s-%s for loc: %s>"%(self.rt_from_address,
                                                        self.rt_to_address,
                                                        self.lt_from_address,
                                                        self.lt_to_address,
                                                        self.loc_id)


class Cleaning(db.Model):
    """Individdual cleanings"""

    __tablename__ = "cleanings"

    cleaning_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    loc_id = db.Column(db.Integer, db.ForeignKey('locations.loc_id'))
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)
    week_of_mon = db.Column(db.Integer, nullable=False)
    day_id = db.Column(db.String(4), db.ForeignKey('days.day_id'))

    location = db.relationship('Location', backref='cleanings')
    day = db.relationship('Day', backref='cleanings')

    def __repr__ (self):
        """Displayed when called"""

        return "<loc-id: %s, starts: %s, ends:%s>"%(self.loc_id,
                                                    self.start_time,
                                                    self.end_time)


class Day (db.Model):
    """Days of week"""

    __tablename__ = "days"

    day_id = db.Column(db.String(4), primary_key=True)
    day_name = db.Column(db.String(9), nullable=False)
    day_short = db.Column(db.String(2), nullable=False)

    def __repr__ (self):
        """Displayed when called"""

        return "<%s>"%(self.day_name)



class User(db.Model):
    """User information"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(11))

    def __repr__ (self):
        """Displayed when called"""

        return "<user-id: %s, email: %s>"%(self.user_id, 
                                           self.email)


class FaveLocation(db.Model):
    """Association table with favorite locations of users"""

    __tablename__ = "favelocations"

    fl_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    address = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    loc_id = db.Column(db.Integer, db.ForeignKey('locations.loc_id'))
    type_id = db.Column(db.String(3), db.ForeignKey('types.type_id'))

    location = db.relationship('Location', backref='fls')
    user = db.relationship('User', backref='fls')
    typed = db.relationship('Type', backref='fls')

    def __repr__ (self):
        """Displayed when called"""

        return "<fl-id: %s, user-id: %s, loc-id: %s>"%(self.fl_id, 
                                                       self.user_id, 
                                                       self.loc_id)

class Type(db.Model):
    """Types of favorite places"""

    __tablename__ = "types"

    type_id = db.Column(db.String(3), primary_key=True)
    type_name = db.Column (db.String(4), nullable=False)

    def __repr__ (self):
        """Displayed when called"""

        return "<%s>"%(self.type_name)


class MessageToSend(db.Model):
    """Messages waiting to be sent"""

    __tablename__ = "messages"

    message_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    time = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref='messages') 

    def __repr__ (self):
        """Displayed when called"""

        return "<id: %s, user-id: %s, time: %s>"%(self.message_id, 
                                                  self.user_id, 
                                                  self.time)

class Tow_Location(db.Model):
    """Unique tow locations"""

    __tablename__ = "tow_locations"

    tow_loc_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    street_id = db.Column(db.Integer, db.ForeignKey('streets.street_id'))
    rt_from_address = db.Column(db.Integer, nullable=False)
    rt_to_address = db.Column(db.Integer, nullable=False)
    lt_from_address = db.Column(db.Integer, nullable=False)
    lt_to_address = db.Column(db.Integer, nullable=False)
    tow_side_id = db.Column(db.Integer, db.ForeignKey('tow_sides.tow_side_id'))
    
    tow_side = db.relationship('Tow_Side', backref='tow_locations')
    street = db.relationship('Street', backref='tow_locations')

    def __repr__ (self):
        """Displayed when called"""

        return "<rt: %s-%s, lt: %s-%s for loc: %s>"%(self.rt_from_address,
                                                        self.rt_to_address,
                                                        self.lt_from_address,
                                                        self.lt_to_address,
                                                        self.tow_loc_id)
class Towing(db.Model):
    """Individdual towings"""

    __tablename__ = "towings"

    towing_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tow_loc_id = db.Column(db.Integer, db.ForeignKey('tow_locations.tow_loc_id'))
    start_time = db.Column(db.String(20), nullable=False)
    day_id = db.Column(db.String(4), db.ForeignKey('days.day_id'))

    tow_location = db.relationship('Tow_Location', backref='towings')
    day = db.relationship('Day', backref='towings')

    def __repr__ (self):
        """Displayed when called"""

        return "< towing for loc-id: %s>"%(self.tow_loc_id)

class Tow_Side(db.Model):
    """sides for towing"""

    __tablename__ = "tow_sides"

    tow_side_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tow_side_name = db.Column(db.String(5), nullable=False)

    def __repr__ (self):
        """Displayed when called"""

        return "<%s>"%(self.tow_side_name)


def example_data():
    password = "boo"
    password = password.encode('utf8') 
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    user = User(email = "kristine", password = hashed)
    user2 = User(email = "kristine", password = hashed, phone='8183333333')
    street = Street(street_id = 1, street_name = "California st")
    street2 = Street(street_id = 2, street_name = "Sacramento st")
    street3 = Street(street_id = 3, street_name = "Lake")
    side = Side(side_id = 1, side_name = "North")
    side2 = Side(side_id = 2, side_name = "South")
    location = Location (loc_id = 1, street_id = 1, 
                         rt_from_address = 0,
                         rt_to_address = 100,
                         lt_from_address = 1,
                         lt_to_address = 1001,
                         side_id = 1,
                         lng_lat = [[38, -12], [38, -12]])
    location2 = Location (loc_id = 2, street_id = 2, 
                         rt_from_address = 0,
                         rt_to_address = 100,
                         lt_from_address = 1,
                         lt_to_address = 1001,
                         side_id = 2,
                         lng_lat = [[38, -12], [38, -12]])
    location3 = Location (loc_id = 3, street_id = 2, 
                         rt_from_address = 5000,
                         rt_to_address = 5006,
                         lt_from_address = 5001,
                         lt_to_address = 5007,
                         side_id = 2,
                         lng_lat = [[38, -12], [38, -12]])
    location4 = Location (loc_id = 4, street_id = 3, 
                         rt_from_address = 0,
                         rt_to_address = 100,
                         lt_from_address = 1,
                         lt_to_address = 1001,
                         lng_lat = [[38, -12], [38, -12]])
    cleaning = Cleaning(loc_id = 1,
                        start_time = '19:00',
                        end_time = '20:00',
                        week_of_mon = 3,
                        day_id = 'Thu')
    cleaning2 = Cleaning(loc_id = 2,
                        start_time = '8:00',
                        end_time = '13:00',
                        week_of_mon = 3,
                        day_id = 'Fri')
    cleaning3 = Cleaning(loc_id = 3,
                        start_time = '8:00',
                        end_time = '20:00',
                        week_of_mon = 3,
                        day_id = 'Thu')
    cleaning4 = Cleaning(loc_id = 3,
                        start_time = '8:00',
                        end_time = '20:00',
                        week_of_mon = 3,
                        day_id = 'Fri')
    cleaning5 = Cleaning(loc_id = 2,
                        start_time = '8:00',
                        end_time = '13:00',
                        week_of_mon = 3,
                        day_id = 'Mon')

    day = Day(day_id = 'Thu', day_name = 'Thursday')
    day2 = Day(day_id = 'Fri', day_name ='Friday')
    day3 = Day(day_id = 'Mon', day_name ='Monday')
    type1 = Type(type_id="hom", type_name="home")
    type2 = Type(type_id="wor", type_name="work")
    type3 = Type(type_id="las", type_name="last")
    db.session.add_all([day, day2, cleaning, cleaning2, 
                        location, location2, side, street, 
                        user, street2, side2, location3,
                        cleaning3, user2, street3, location4,
                        type2, type3, type1, cleaning4, cleaning5, day3])
    db.session.commit()

def connect_to_db(app, db_uri = "postgres:///parking"):
    """Connect the database to Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    app = Flask(__name__)
    connect_to_db(app)
    print "Connected to DB."
