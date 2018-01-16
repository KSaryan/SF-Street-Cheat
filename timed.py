import schedule
import time
from datetime import datetime, timedelta
from model import (User, MessageToSend, connect_to_db, db)
import os
from twilio.rest import Client
import sendgrid
from sendgrid.helpers.mail import *
import logging


LOG_FILENAME = 'failed_messages.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

# connect_to_db(app)

def job():
    time = datetime.now() + timedelta(minutes=30)
    messages = MessageToSend.query.filter(MessageToSend.time <= time).all()
    for m in messages:
        user = User.query.get(m.user_id)
        time = m.time.strftime('%H:%M')
        number = '(' + user.phone[:3] + ')' + user.phone[3:6] + '-' + user.phone[6:]
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token  = os.environ['TWILIO_AUTH_TOKEN']

        client = Client(account_sid, auth_token)

        try: 
            message = client.messages.create(
                to=user.phone, 
                from_=os.environ['TWILIO_NUMBER'],
                body="Move your car by " + time + " (military time)")
                #could make this dynamic
                # status_callback='http://localhost:5000/twilio_callbacks')
        except:
            try:
                email = user.email
                sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
                from_email = Email("noreply@streetcheat.com")
                to_email = Email(email)
                subject = "Parking Notification"
                content = Content("text/plain", "We attempted to send a text reminder to " + number +
                                  ". However, the number was invalid. \nMake sure to move you car by " +
                                  time + ".\nAnd don't forget to update your account!")
                mail = Mail(from_email, subject, to_email, content)
                response = sg.client.mail.send.post(request_body=mail.get())
            except:
                logging.warn("failed to send message to user " + str(m.user_id))
        db.session.delete(m)
        db.session.commit()

def schedule_cron():
    schedule.every(20).minutes.do(job)

    while 1:
        schedule.run_pending()
        time.sleep(1)
