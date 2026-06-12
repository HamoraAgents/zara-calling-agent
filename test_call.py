from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'), 
    os.getenv('TWILIO_AUTH_TOKEN')
)

call = client.calls.create(
    url='https://hardhead-overreach-unfitted.ngrok-free.app/voice',
    to='+923045257986',
    from_='+13186603080'
)

print('Call ho rahi hai!')