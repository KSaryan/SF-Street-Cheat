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


# def create_cleaning_weeks():
#     """Creates entry in cleaningweeks table"""
#     pass