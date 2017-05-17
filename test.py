import os 
from twilio.rest import Client

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token  = os.environ['TWILIO_AUTH_TOKEN']

client = Client(account_sid, auth_token)

try:
    message = client.messages.create(
        to='818216335', 
        from_=os.environ['TWILIO_NUMBER'],
        #need to make message better
        body="Move your car.")
        #could make this dynamic
        # status_callback='http://localhost:5000/twilio_callbacks')
except:
    print "oops"

print "doing next thing"