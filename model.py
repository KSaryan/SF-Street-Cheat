from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
import pytz
# from server import app

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


class Location(db.Model):
    """Specific address."""

    __tablename__ = "locations"

    loc_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    street_id = db.Column(db.Integer, db.ForeignKey('streets.street_id'))
    rt_from_address = db.Column(db.Integer, nullable=False)
    rt_to_address = db.Column(db.Integer, nullable=False)
    lt_from_address = db.Column(db.Integer, nullable=False)
    lt_to_address = db.Column(db.Integer, nullable=False)
    side_id = db.Column(db.Integer, db.ForeignKey('sides.side_id'))

    sides = db.relationship('Side', backref='locations')
    streets = db.relationship('Street', backref='locations')

    def __repr__ (self):
        """Displayed when called"""

        return "<rt: %s-%s, lt: %s-%s for loc: %s>"%(self.rt_from_address,
                                                        self.rt_to_address,
                                                        self.lt_from_address,
                                                        self.lt_to_address,
                                                        self.loc_id)

    @classmethod
    def get_unique(cls, street_id, rt_to_address, lt_to_address, side_id):
        cache = db.session._unique_cache = getattr(db.session, '_unique_cache', {})

        key = (cls, street_id, rt_to_address, lt_to_address, side_id)
        o = cache.get(key)
        if o is None:
            o = db.session.query(cls).filter(cls.street_id==street_id, 
                                          cls.rt_to_address==rt_to_address, 
                                          cls.lt_to_address==lt_to_address,
                                          cls.side_id==side_id).first()
            if o is None:
                return True


class Cleaning(db.Model):
    """Individdual cleanings"""

    __tablename__ = "cleanings"

    cleaning_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    loc_id = db.Column(db.Integer, db.ForeignKey('locations.loc_id'))
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)
    week_of_mon = db.Column(db.Integer, nullable=False)
    day_id = db.Column(db.String(4), db.ForeignKey('days.day_id'))

    locations = db.relationship('Location', backref='cleanings')
    days = db.relationship('Day', backref='cleanings')

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

    def __repr__ (self):
        """Displayed when called"""

        return "<%s>"%(self.day_name)



class User(db.Model):
    """User information"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(11))

    def __repr__ (self):
        """Displayed when called"""

        return "<user-id: %s, email: %s>"%(self.user_id, 
                                           self.email)


class FaveLocation(db.Model):
    """Association table with favorite locations of users"""

    __tablename__ = "favelocations"

    fl_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    loc_id = db.Column(db.Integer, db.ForeignKey('locations.loc_id'))

    locations = db.relationship('Location', backref='fls')
    users = db.relationship('User', backref='fls')

    def __repr__ (self):
        """Displayed when called"""

        return "<fl-id: %s, user-id: %s, loc-id: %s>"%(self.fl_id, 
                                                       self.user_id, 
                                                       self.loc_id)

class MessagesToSend(db.Model):
    """Messages waiting to be sent"""

    __tablename__ = "messages"

    message_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    time = db.Column(db.DateTime, nullable=False)

    users = db.relationship('User', backref='messages') 

    def __repr__ (self):
        """Displayed when called"""

        return "<id: %s, user-id: %s, time: %s>"%(self.message_id, 
                                                  self.user_id, 
                                                  self.time)


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
                    return ["later today", hours]
                elif int(end_time.strftime("%H")) < int(now.strftime("%H")):
                    return "Street cleaning is now"
        
    while True:
        now = now + timedelta(days=1)
        day = now.strftime("%a")
        if day == "Thu":
            day = "Thur"
        date = int(now.strftime("%d"))
        week_of_mon = (date / 7) + 1
        for cleaning in street_cleanings:
            if cleaning.week_of_mon == week_of_mon and cleaning.day_id == day:
                        # next_cleaning = cleaning
                        return [now, cleaning]
        


def connect_to_db(app):
    """Connect the database to Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///parking'
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    #can import app from server later
    app = Flask(__name__)
    connect_to_db(app)
    print "Connected to DB."