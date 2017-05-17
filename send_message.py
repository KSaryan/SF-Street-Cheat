from twilio.rest import Client
import os

account_sid = os.environ['TWILIO_ACOUNT_SID']
auth_token  = os.environ['TWILIO_AUTH_TOKEN']

client = Client(account_sid, auth_token)

message = client.messages.create(
    to="8185216335", 
    from_="+18056284802",
    body="Hello from Python!")

print(message.sid)