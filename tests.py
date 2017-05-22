from unittest import TestCase
from model import (Location, Cleaning, Day, User, Side, 
                   Street, FaveLocation, MessageToSend, connect_to_db, db, example_data)
from server import app
from datetime import date, datetime
import helpers

class MyAppUnitTestCase(TestCase):
    def setUp(self):
        self.client =app.test_client()
        app.config["TESTING"] = True
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        example_data()
        now = (2017, 5, 18, 18, 3, 3, 963267)

    def tearDown(self):
        """Do at end of every test."""

        db.drop_all()
        db.session.close()

    def test_get_sides(TestCase):
        assert helpers.get_sides_for_this_location('California', '50') == 'North'

    def test_find_next_cleaning(self):
        cleanings = Cleaning.query.get(1)
        assert helpers.find_nect_cleaning(cleanings, now) == "blag"
#     def test_find_location(self):
#         assert helpers.find_location(50, 'California', 'North') == '<rt: 0-100, lt: 1-1001 for loc: 1>'
#         # assert helpers.find_location(50, 'Lake') == object

class TestRoutesLogedIn(TestCase):
    def setUp(self):
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
        

    def test_homepage_loged_in(self):
        result = self.client.get('/', follow_redirects=True)
        self.assertIn("How Long Until Street Cleaning", result.data)

    def test_homepage_loged_in(self):
        result = self.client.post('/', follow_redirects=True)
        self.assertIn("Welcome! Login to use.", result.data)

    def test_parking_loged_in(self):
        result = self.client.get('/parking')
        self.assertIn("How Long Until Street Cleaning", result.data)

    def test_user_info_loged_in(self):
        result = self.client.get('/user_info')
        self.assertIn("User information for", result.data)

    def test_update_user(self):
        result = self.client.post('/update_user', 
                                 data={'email':"ksaryan3", 'password':'boo', 'number':'818555-3333'},
                                 follow_redirects=True)

        self.assertIn("ksaryan3", result.data)
        self.assertIn('(818) 555 - 3333', result.data)


class TestRoutesLogedOut(TestCase):
    def setUp(self):
        self.client =app.test_client()
        app.config["TESTING"] = True
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        example_data()
        
    def tearDown(self):
        """Do at end of every test."""

        db.drop_all()
        db.session.close()

    def test_homepage_loged_in(self):
        result = self.client.get('/')
        self.assertIn("Welcome! Login to use.", result.data)

    def test_parking_loged_in(self):
        result = self.client.get('/parking', follow_redirects=True)
        self.assertIn("Welcome! Login to use.", result.data)

    def test_user_info_loged_in(self):
        result = self.client.get('/user_info', follow_redirects=True)
        self.assertIn("Welcome! Login to use.", result.data)

    def test_user_verify(self):
        result = self.client.post('/verify_user', 
                                  data={'email': 'ksaryan', 'password':'boo'}, 
                                  follow_redirects=True)
        self.assertIn("How Long Until Street Cleaning", result.data)

    def test_user_verify(self):
        result = self.client.post('/create_user', 
                                  data={'email': 'ksaryan1', 'password':'boo2'}, 
                                  follow_redirects=True)
        self.assertIn("How Long Until Street Cleaning", result.data)

class TestRoutesWithMoc(TestCase):
    def setUp(self):
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
        result = self.client.get('/street_cleaning.json',
                                 query_string={'address':'50', 'street':'California', 'side':'North'})
        self.assertIn('Street cleaning is today. It\'s in 1 hours.', result.data)

    def test_street_cleaning_tomorrow(self):
        result = self.client.get('/street_cleaning.json',
                                 query_string={'address':'50', 'street':'Sacramento', 'side':'South'})
        self.assertIn('Next cleaning is in 1 days', result.data)
    
    def test_street_cleaning_now(self):
        result = self.client.get('/street_cleaning.json',
                                 query_string={'address':'5002', 'street':'Sacramento', 'side':'South'})
        self.assertIn('Street cleaning is now', result.data)

    def test_street_cleaning_wrong_address(self):
        result = self.client.get('/street_cleaning.json',
                                 query_string={'address':'3000', 'street':'Sacramento', 'side':'South'})
        self.assertIn('Not a valid address', result.data)

    def test_find_sides(self):
        result = self.client.get('/find_sides.json',
                                 query_string={'address':'50', 'street':'California' })
        self.assertIn('North', result.data)
        self.assertNotIn('South', result.data)

class TestUser1Text(TestCase):
    def setUp(self):
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
        result = self.client.post('/send_text.json',
                                 data={"cleaningtime": datetime(2017, 5, 18, 18, 3, 3, 963267)})
        self.assertIn('False', result.data)


class TestUser2Text(TestCase):
    def setUp(self):
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
        result = self.client.post('/send_text.json',
                                 data={"cleaningtime": datetime(2017, 5, 18, 18, 3, 3, 963267)})
        self.assertIn('True', result.data)


if __name__ == "__main__":
    import unittest

    unittest.main()
