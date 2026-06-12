from groq import Groq
from dotenv import load_dotenv
import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from flask import Flask, request
import re

# Load Environment
load_dotenv()

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
                "content": """You are Zara, a professional AI voice assistant from HamoraAgents.

STRICT RULES:
- Always reply in English only
- Keep responses very short — max 2 sentences
- Be natural and professional
- No asterisk or special characters
- You are on a phone call — be conversational

IDENTITY:
- Your name is Zara
- You are AI voice assistant from HamoraAgents
- You help businesses with customer calls"""
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
        "Hello! I am Zara from HamoraAgents. How can I help you today?",
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
        print(f"\nUser: {user_speech}")
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
    print("\n⚡ Zara Call Agent Ready!")
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