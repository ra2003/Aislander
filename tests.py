""" Test file for Flask routes and database. """

# import library used for user tests
from unittest import TestCase

# import example_data function only
from model import connect_to_db, db, example_data, User, Bookmark

from server import app
from flask import session


###################### LOG IN / LOG OUT / REGISTRATION ####################

class FlaskTestsLogInLogOutRegistration(TestCase):
    """Test log in and log out."""

    def setUp(self):
        """Before every test"""

        app.config['TESTING'] = True
        self.client = app.test_client()

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_correct_login_page(self):
        """ Test that login page properly showing login form. """

        result = self.client.get('/login')
        self.assertIn("<h2> Login form </h2>", result.data)

    def test_correct_registration_page(self):
        """ That that registration page properly showing registration form. """

        result = self.client.get('/register')
        self.assertIn("<h2> Registration form </h2>", result.data)

    def test_correct_login(self):
        """Test log in form with correct info."""

        with self.client as c:
            result = c.post('/login',
                            data={'username': 'Bob', 'password': 'Bobpw'},
                            follow_redirects=True
                            )

            self.assertEqual(session['user_id'], 1)
            self.assertIn("Bob has successfully logged in.", result.data)

    def test_incorrect_username(self):
        """Test log in form with purposefully wrong username."""

        with self.client as c:
            result = c.post('/login',
                            data={'username': 'char', 'password': 'Bobpw'},
                            follow_redirects=True
                            )

            self.assertIn("char does not exist!", result.data)
            self.assertNotIn("char has successfully logged in.", result.data)

    def test_incorrect_password(self):
        """Test log in form with purposefully wrong password."""

        with self.client as c:
            result = c.post('/login',
                            data={'username': 'Bob', 'password': 'pw'},
                            follow_redirects=True
                            )

            self.assertIn("Incorrect password", result.data)

    def test_logout(self):
        """Test logout route."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '1'

            result = self.client.get('/logout', follow_redirects=True)

            self.assertNotIn('user_id', session)
            self.assertIn('You have logged out.', result.data)

    def test_registration_correct_info(self):
        """ Test that user successfully registers upon form submission. """

        with self.client as c:
            result = c.post('/register',
                            data={'username': 'Char',
                                  'email': 'Char@gmail.com',
                                  'password': 'Char1'},
                            follow_redirects=True
                            )

            # Check that success message appears
            self.assertIn("Thanks for registering Char!", result.data)

            # Check that info gets stored in DB
            current_user = User.query.filter(User.username == 'Char').first()
            self.assertIsNotNone(current_user)

    def test_registration_incorrect_info(self):
        """ Test that user gets error message upon already-taken username. """

        with self.client as c:
            result = c.post('/register',
                            data={'username': 'Bob',
                                  'email': 'bob@gmail.com',
                                  'password': 'Bobpw'},
                            follow_redirects=True
                            )

            # Check that success message appears
            self.assertIn("Bob already taken. Try again!", result.data)
            self.assertNotIn("Thanks for registering Bob!", result.data)

            # Check that info does not get stored in DB
            current_user = User.query.filter(User.username == 'Bob').count()
            self.assertNotEqual(2L, current_user)


########################## USER PROFILE PAGE ###############################

class FlaskTestsUserProfile(TestCase):
    """Test user profile page."""

    def setUp(self):
        """Before every test"""

        app.config['TESTING'] = True
        self.client = app.test_client()

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_correct_page(self):
        """ Test that correct page is showing up. """

        result = self.client.get('/users/Bob')
        self.assertIn("User Profile", result.data)
        self.assertNotIn("Dashboard", result.data)
        self.assertNotIn("Homepage", result.data)
        self.assertNotIn("Recipe Info", result.data)
        self.assertNotIn("Login Form", result.data)
        self.assertNotIn("Registration Form", result.data)

    def test_correct_username(self):
        """ Test correct username is showing on the page. """

        result = self.client.get('/users/Bob')
        self.assertIn("Bob", result.data)
        self.assertNotIn("Jane", result.data)

    def test_correct_email(self):
        """ Test that correct email is showing on the page. """

        result = self.client.get('/users/Bob')
        self.assertIn("bob@gmail.com", result.data)
        self.assertNotIn("jane@gmail.com", result.data)

    def test_correct_bookmarks(self):
        """ Test that correct bookmarked recipes is showing on the page. """

        result = self.client.get('/users/Bob')
        self.assertIn("Thai Sweet Potato", result.data)
        self.assertNotIn("Meatless Burgers with Romesco and Arugula", result.data)

######################### INITIAL DASHBOARD PAGE ##############################


class FlaskTestsDashboard(TestCase):
    """Test dashboard page."""

    def setUp(self):
        """Before every test"""

        app.config['TESTING'] = True
        self.client = app.test_client()

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_correct_info(self):
        """ Test that what is supposed to show up in page is indeed showing. """

########################## BOOKMARK FEATURE ###############################


class FlaskTestsBookmark(TestCase):
    """Test bookmark feature."""

    def setUp(self):
        """Before every test"""

        app.config['TESTING'] = True
        self.client = app.test_client()

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_already_existing_bookmark(self):
        """ Test if error message appears with already-bookmarked recipe. """

        with self.client as c:
            result = c.post('/bookmark.json',
                            data={'recipe_id': '262682'},
                            follow_redirects=True
                            )

            self.assertIn("You've already bookmarked this recipe.", result.data)

    def test_new_bookmark(self):
        """ Test if success message appears with bookmarking a new recipe. """

        # Check that bookmark did not exist before
        check = Bookmark.query.filter((Bookmark.recipe_id == '227961') & (Bookmark.user_id == 1)).first()
        self.assertIsNone(check)

        with self.client as c:
            result = c.post('/bookmark.json',
                            data={'recipe_id': '227961'},
                            follow_redirects=True
                            )

            # Check that success message appears
            self.assertIn("This recipe has been bookmarked!", result.data)

            # Check that new bookmark now successfully added
            current_bookmark = Bookmark.query.filter((Bookmark.recipe_id == '227961') & (Bookmark.user_id == 1)).one()
            self.assertIsNotNone(current_bookmark)

    def test_existing_bookmark(self):
        """ Test if error message appears with an already-bookmarked recipe. """

        with self.client as c:
            result = c.post('/bookmark.json',
                            data={'recipe_id': '262682'},
                            follow_redirects=True
                            )

            # Check that error message appears
            self.assertIn("You've already bookmarked this recipe.", result.data)

            # Check that bookmark does not get duplicated in DB
            current_bookmark = Bookmark.query.filter((Bookmark.recipe_id == '262682') & (Bookmark.user_id == 1)).count()
            self.assertEqual(1L, current_bookmark)


if __name__ == "__main__":
    import unittest

    unittest.main()