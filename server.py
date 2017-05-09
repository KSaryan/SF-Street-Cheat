from jinja2 import StrictUndefined

from flask import jsonify
from flask import (Flask, render_template, redirect, request, flash,
                   session, url_for)

from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import update

from model import (Location, Cleaning, CleaningDay, Day, CleaningWeek, 
                   Week, User, FaveLocation, connect_to_db, db)

app = Flask(__name___)

