from groq import Groq
from dotenv import load_dotenv
import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from flask import Flask, request
import re
import json

# Load Environment
load_dotenv()

# Pharmacy Data Load
with open('medicines.json', 'r') as f:
    pharmacy_data = json.load(f)

# Clients
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

# Flask App
app = Flask(__name__)

# Conversation History
conversation_history = {}

# Clean Text
def clean_text(text):
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'#+', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    return text.strip()

# AI Response
def get_ai_response(call_sid, user_input):
    if call_sid not in conversation_history:
        conversation_history[call_sid] = [
            {
                "role": "system",
                "content": f"""You are Zara, AI pharmacy assistant for {pharmacy_data['pharmacy_name']}.

PHARMACY INFO:
- Name: {pharmacy_data['pharmacy_name']}
- Location: {pharmacy_data['location']}
- Timing: {pharmacy_data['timing']}
- Contact: {pharmacy_data['contact']}

MEDICINES LIST:
{json.dumps(pharmacy_data['medicines'], indent=2)}

YOUR JOB:
- Tell if medicine is available or not
- Tell price of medicines
- Help with appointment booking
- Be professional and friendly
- Reply in English only
- Keep responses short — max 2 sentences
- No asterisk or special characters

IF MEDICINE NOT IN LIST:
Say: Please visit our pharmacy or call us directly.

IDENTITY:
- Your name is Zara
- You are AI assistant of {pharmacy_data['pharmacy_name']}
- You are available 24/7"""
            }
        ]

    conversation_history[call_sid].append({
        "role": "user",
        "content": user_input
    })

    chat = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=conversation_history[call_sid],
        max_tokens=100,
        temperature=0.7
    )

    response = clean_text(chat.choices[0].message.content)

    conversation_history[call_sid].append({
        "role": "assistant",
        "content": response
    })

    return response

# Welcome Call
@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/respond",
        timeout=5,
        speech_timeout="auto",
        language="en-US"
    )
    gather.say(
        f"Hello! I am Zara, AI assistant from {pharmacy_data['pharmacy_name']}. How can I help you today?",
        voice="Polly.Joanna"
    )
    response.append(gather)
    return str(response)

# Handle Response
@app.route("/respond", methods=["POST"])
def respond():
    call_sid = request.form.get("CallSid")
    user_speech = request.form.get("SpeechResult", "")

    response = VoiceResponse()

    if user_speech:
        ai_response = get_ai_response(call_sid, user_speech)
        print(f"\nCustomer: {user_speech}")
        print(f"Zara: {ai_response}")

        gather = Gather(
            input="speech",
            action="/respond",
            timeout=5,
            speech_timeout="auto",
            language="en-US"
        )
        gather.say(ai_response, voice="Polly.Joanna")
        response.append(gather)
    else:
        gather = Gather(
            input="speech",
            action="/respond",
            timeout=5,
            speech_timeout="auto",
            language="en-US"
        )
        gather.say(
            "I did not hear you. Could you please repeat?",
            voice="Polly.Joanna"
        )
        response.append(gather)

    return str(response)

# Main
if __name__ == "__main__":
    public_url = "https://hardhead-overreach-unfitted.ngrok-free.app"

    print(f"\n✅ Ngrok URL: {public_url}")
    print(f"✅ Webhook: {public_url}/voice")
    print(f"\n⚡ {pharmacy_data['pharmacy_name']} Agent Ready!")
    print("=" * 45)

    twilio_client.incoming_phone_numbers.list(
        phone_number=os.getenv("TWILIO_PHONE_NUMBER")
    )[0].update(
        voice_url=f"{public_url}/voice"
    )

    print(f"✅ Twilio Webhook Set!")
    print(f"📞 Call karo: {os.getenv('TWILIO_PHONE_NUMBER')}")
    print("=" * 45)

    app.run(port=5000)