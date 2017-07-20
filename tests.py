from unittest import TestCase
from model import (Location, Cleaning, Day, User, Side, 
                   Street, FaveLocation, MessageToSend, connect_to_db, db, example_data)
from server import app
from datetime import date, datetime
import helpers
from pytz import timezone

class MyAppUnitTestCase(TestCase):
    """class for unittests"""

    def setUp(self):
        """Do at beginning of every test"""

        self.client =app.test_client()
        app.config["TESTING"] = True
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        example_data()
        self.now = datetime(2017, 5, 18, 18, 3, 3, 963267)
        localtz = timezone('US/Pacific')
        self.now = localtz.localize(self.now)
        self.cleanings = Cleaning.query.filter_by(loc_id=3).all()
        self.cleanings2 = Cleaning.query.filter_by(loc_id=2).all()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()
        

    def test_get_sides(self):
        """tests get_sides function in helpers"""

        self.assertEqual(['North'], helpers.get_sides_for_this_location('California st', '50'))

  
    def test_find_todays_cleaning(self):
        """tests find_todays_cleaning function in helpers"""

        self.assertIn("now", (helpers.find_todays_cleaning(self.cleanings, self.now))[0])


    def test_find_next_cleaning(self):
        """tests find_next_cleaning in helpers"""

        self.assertIn("Friday", (helpers.find_next_cleaning(self.cleanings, self.now))[1])
        
   
    def test_find_location(self):
        """tests find_location in helpers"""

        self.assertEqual(str(helpers.find_location(50, 'California st', 'North')), '<rt: 0-100, lt: 1-1001 for loc: 1>')


class TestRoutesLogedIn(TestCase):
    """Tests routes as user loged in"""

    def setUp(self):
        """Do at beginning of every test"""

        self.client = app.test_client()
        app.config["TESTING"] = True
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        example_data()
        with self.client as c:
          with c.session_transaction() as sess:
              sess['login'] = 1

    def tearDown(self):
        """Do at end of every test."""

        db.drop_all()
        db.session.close()
        

    def test_homepage_loged_in(self):
        """tests index route as a get request"""

        result = self.client.get('/', follow_redirects=True)
        self.assertIn("How Long Until Street Cleaning", result.data)

    def test_homepage_loged_in(self):
        """tests index route as a post request (logging out user)"""

        result = self.client.post('/', follow_redirects=True)
        self.assertIn("Don't Let Street Cleaning Ruin Your Day", result.data)

    def test_login_loged_in(self):
        """tests login route"""

        result = self.client.get('/login', follow_redirects=True)
        self.assertIn("How Long Until Street Cleaning", result.data)

    def test_parking_loged_in(self):
        """tests parking route"""

        result = self.client.get('/parking')
        self.assertIn("How Long Until Street Cleaning", result.data)
        self.assertIn("Get A Text Reminder", result.data)

    def test_my_places_loged_in(self):
        """test my_places route"""

        result = self.client.get('/my_places')
        self.assertIn("Recent", result.data)

    def test_user_info_loged_in(self):
        """tests user_info route"""

        result = self.client.get('/user_info')
        self.assertIn("User information for", result.data)

    def test_update_user(self):
        """tests uodate_user route"""

        result = self.client.post('/update_user', 
                                 data={'email':"ksaryan3", 'password':'boo', 'number':'818555-3333'},
                                 follow_redirects=True)

        self.assertIn("ksaryan3", result.data)
        self.assertIn('(818) 555 - 3333', result.data)

    #failing
    def test_add_fave_loc(self):
        """tests add_fave_loc route"""

        result = self.client.get('/add_fave_loc', 
                                 query_string={'street':'California-st', 'address':'50', 'side':'North', 'typefave':'wor'}, 
                                 follow_redirects=True)
        self.assertIn('50 California st', result.data)


class TestRoutesLogedOut(TestCase):
    """Tests routes as user loged out"""

    def setUp(self):
        """Do at beginning of every test"""

        self.client =app.test_client()
        app.config["TESTING"] = True
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        example_data()
        
    def tearDown(self):
        """Do at end of every test."""

        db.drop_all()
        db.session.close()

    def test_parking_loged_out(self):
        """tests parking route"""

        result = self.client.get('/parking', follow_redirects=True)
        self.assertIn("login", result.data)
        self.assertIn("Login to Get Text Reminders", result.data)

    def test_my_places_loged_out(self):
        """tests my_places route"""

        result = self.client.get('/my_places', follow_redirects=True)
        self.assertNotIn("Recent", result.data)
        self.assertIn("Please login to use", result.data)

    def test_user_info_loged_out(self):
        """tests user_info route"""

        result = self.client.get('/user_info', follow_redirects=True)
        self.assertIn("Register", result.data)

    #failing
    def test_user_verify(self):
        """tests verify_user route"""

        result = self.client.post('/verify_user', 
                                  data={'email': 'ksaryan', 'password':'boo'}, 
                                  follow_redirects=True)
        self.assertIn("How Long Until Street Cleaning", result.data)

    def test_create_user(self):
        """tests create_user route"""

        result = self.client.post('/create_user', 
                                  data={'email': 'ksaryan1', 'password':'boo2'}, 
                                  follow_redirects=True)
        self.assertIn("How Long Until Street Cleaning", result.data)

class TestRoutesWithMoc(TestCase):
    """Tests routes with user loged in and mock function for time"""

    def setUp(self):
        """Do at beginning of every test"""

        self.client =app.test_client()
        app.config["TESTING"] = True
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        example_data()
        def _mock_date_time():
            return datetime(2017, 5, 18, 18, 3, 3, 963267)

        helpers.get_datetime = _mock_date_time
        with self.client as c:
            with c.session_transaction() as sess:
                sess['login'] = 1

    def tearDown(self):
        """Do at end of every test."""

        db.drop_all()
        db.session.close()
        

    def test_street_cleaning(self):
        """tests street_cleaning route"""

        result = self.client.get('/street_cleaning.json',
                                 query_string={'address':'50', 'street':'California st', 'side':'North'})
        self.assertIn('Street cleaning is today. It\'s in 1 hours.', result.data)

    def test_street_cleaning_tomorrow(self):
        """tests street_cleaning route"""

        result = self.client.get('/street_cleaning.json',
                                 query_string={'address':'50', 'street':'Sacramento st', 'side':'South'})
        self.assertIn('Next cleaning is in 1 days', result.data)
    
    def test_street_cleaning_now(self):
        """tests street_cleaning route"""

        result = self.client.get('/street_cleaning.json',
                                 query_string={'address':'5002', 'street':'Sacramento st', 'side':'South'})
        self.assertIn('Street cleaning is now', result.data)

    def test_street_cleaning_wrong_address(self):
        """tests street_cleaning route"""

        result = self.client.get('/street_cleaning.json',
                                 query_string={'address':'3000', 'street':'Sacramento st', 'side':'South'})
        self.assertIn('Not a valid address', result.data)

    def test_find_sides(self):
        """tests find_sides route"""

        result = self.client.get('/find_sides.json',
                                 query_string={'address':'50', 'street':'California st' })
        self.assertIn('North', result.data)
        self.assertNotIn('South', result.data)


class TestUser1Text(TestCase):
    def setUp(self):
        """Do at beginning of every test"""

        self.client =app.test_client()
        app.config["TESTING"] = True
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        example_data()
        with self.client as c:
            with c.session_transaction() as sess:
                sess['login'] = 1

    def tearDown(self):
        """Do at end of every test."""

        db.drop_all()
        db.session.close()

    def test_send_text(self):
        """tests send_text route for user with no number"""

        result = self.client.post('/send_text.json',
                                 data={"cleaningtime": datetime(2017, 5, 18, 18, 3, 3, 963267)})
        self.assertIn('False', result.data)


class TestUser2Text(TestCase):
    def setUp(self):
        """Do at beginning of every test"""

        self.client =app.test_client()
        app.config["TESTING"] = True
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        example_data()
        with self.client as c:
            with c.session_transaction() as sess:
                sess['login'] = 2

    def tearDown(self):
        """Do at end of every test."""

        db.drop_all()
        db.session.close()
        
    def test_send_text(self):
        """tests send_text route for user with number"""

        result = self.client.post('/send_text.json',
                                 data={"cleaningtime": datetime(2017, 5, 18, 18, 3, 3, 963267)})
        self.assertIn('True', result.data)


if __name__ == "__main__":
    import unittest

    unittest.main()
