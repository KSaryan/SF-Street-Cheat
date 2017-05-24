class CleaningWeek(db.Model):
#     """Association table between cleanings and weeks"""

#     __tablename__ = "cleaningweeks"

#     cw_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     week_id = db.Column(db.Integer, db.ForeignKey('weeks.week_id'))
#     loc_id = db.Column(db.Integer, db.ForeignKey('locations.loc_id'))

#     locations = db.relationship('Location', backref='cws')
#     weeks = db.relationship('Week', backref='cws')

#     def __repr__ (self):
#         """Displayed when called"""

#         return "<cw-d: %s, week-id: %s, cleaning-id: %s>"%(self.cw_id, 
#                                                            self.week_id, 
#                                                            self.cleaning_id)


# class Week (db.Model):
#     """Weeks with street cleaning"""

#     __tablename__ = "weeks"

#     week_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     # week_of_mon = db.Column(db.Integer, nullable=False)

#     def __repr__ (self):
#         """Displayed when called"""

#         return "<week of month: %s>"%(self.week_id)

# class CleaningDay(db.Model):
#     """Association table between cleanings and days"""

#     __tablename__ = "cleaningdays"

#     cd_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     day_id = db.Column(db.String(3), db.ForeignKey('days.day_id'))
#     loc_id = db.Column(db.Integer, db.ForeignKey('locations.loc_id'))

#     locations = db.relationship('Location', backref='cds')
#     days = db.relationship('Day', backref='cds')

#     def __repr__ (self):
#         """Displayed when called"""

#         return "<cd-id : %s, day-id: %s, cleaning-id: %s>"%(self.cd_id, 
#                                                             self.day_id, 
#                                                             self.cleaning_id)

# def create_cleaning_days():
#     """Creates entry in cleaning days table"""

#     CleaningDay.query.delete()


#     url = "https://data.sfgov.org/resource/u2ac-gv9v.json?$limit=39000&weekday=Mon"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#     for item in data:
#         street = item["streetname"]
#         rt_to_address = item["rt_toadd"]
#         lt_to_address = item["lf_toadd"]
#         side = item.get("blockside")
#         entry = db.session.query(Location).filter(Location.street==street, 
#                                                   Location.rt_to_address==rt_to_address,
#                                                   Location.lt_to_address==lt_to_address, 
#                                                   Location.side==side).first()

#         loc_id=entry.loc_id
#         cleaningday= CleaningDay(loc_id=loc_id, day_id='Mon')
#         db.session.add(cleaningday)

#     db.session.commit()
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

# def create_cleaning_weeks():
#     """Creates entry in cleaningweeks table"""
#     pass

 # @classmethod
    # def get_unique(cls, street_id, rt_to_address, lt_to_address, side_id):
    #     """Checks if location already in table"""

    #     # cache = db.session._unique_cache = getattr(db.session, '_unique_cache', {})

    #     # key = (cls, street_id, rt_to_address, lt_to_address, side_id)
    #     # o = cache.get(key)
    #     # if o is None:
    #     o = db.session.query(cls).filter(cls.street_id==street_id, 
    #                                       cls.rt_to_address==rt_to_address, 
    #                                       cls.lt_to_address==lt_to_address,
    #                                       cls.side_id==side_id).first()
    #     if o is None:
    #         return True

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
