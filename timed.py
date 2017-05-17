import schedule
import time
from datetime import datetime, timedelta
from model import (User, MessageToSend, connect_to_db, db)
from server import app
import os
from twilio.rest import Client
import requests

connect_to_db(app)

def timed_job():
    def job():
        messages = MessageToSend.query.all()
        for m in messages:
            if datetime.now() + timedelta(minutes=30) >= m.time:
                user = User.query.get(m.user_id)
                account_sid = os.environ['TWILIO_ACCOUNT_SID']
                auth_token  = os.environ['TWILIO_AUTH_TOKEN']

                client = Client(account_sid, auth_token)

                message = client.messages.create(
                    to=user.phone, 
                    from_=os.environ['TWILIO_NUMBER'],
                    #need to make message better
                    body="Move your car.")
                db.session.delete(m)
                db.session.commit()

    schedule.every(20).minutes.do(job)
    print "Sending texts"

    while 1:
        schedule.run_pending()
        time.sleep(1)

timed_job()