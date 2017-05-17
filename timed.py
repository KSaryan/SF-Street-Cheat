import schedule
import time
from datetime import datetime, timedelta
from model import (User, MessageToSend, connect_to_db, db)
from server import app
import os
from twilio.rest import Client
import requests

connect_to_db(app)

def job():
    #could cut down query by just getting message for that day
    #could do if statement in the query
    time = datetime.now() + timedelta(minutes=30)
    messages = MessageToSend.query.filter(MessageToSend.time <= time).all()
    for m in messages:
        # if datetime.now() + timedelta(minutes=30) >= m.time:
        user = User.query.get(m.user_id)
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token  = os.environ['TWILIO_AUTH_TOKEN']

        client = Client(account_sid, auth_token)

        try: 
            message = client.messages.create(
                to=user.phone, 
                from_=os.environ['TWILIO_NUMBER'],
                #need to make message better
                body="Move your car.")
                #could make this dynamic
                # status_callback='http://localhost:5000/twilio_callbacks')
            db.session.delete(m)
            db.session.commit()
        except:
            print "error"

schedule.every(20).minutes.do(job)
print "Sending texts"

while 1:
    schedule.run_pending()
    time.sleep(1)
