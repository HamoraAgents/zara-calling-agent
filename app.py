from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

conversation = [
    {
        "role": "system",
        "content": """You are Zara, a professional AI call agent from HamoraAgents.
RULES:
- Keep responses very short — max 2 sentences
- Be natural and friendly
- English mein baat karo
- No special characters"""
    }
]

@app.route("/answer", methods=["GET", "POST"])
def answer_call():
    response = VoiceResponse()
    gather = Gather(input="speech", action="/process", timeout=3)
    gather.say("Hello! I am Zara from HamoraAgents. How can I help you today?")
    response.append(gather)
    return str(response)

@app.route("/process", methods=["GET", "POST"])
def process_speech():
    user_speech = request.form.get("SpeechResult", "")
    conversation.append({"role": "user", "content": user_speech})
    chat = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=conversation,
        max_tokens=100,
        temperature=0.7
    )
    response_text = chat.choices[0].message.content
    conversation.append({"role": "assistant", "content": response_text})
    response = VoiceResponse()
    gather = Gather(input="speech", action="/process", timeout=3)
    gather.say(response_text)
    response.append(gather)
    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)