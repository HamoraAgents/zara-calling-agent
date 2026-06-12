# Zara — AI Calling Agent 🤖📞

An AI-powered voice calling agent built with Groq, Twilio, and Flask.

## What is Zara?
Zara is an AI voice assistant that handles real phone calls automatically.
Built by HamoraAgents.

---

## Features
- ✅ Real phone call handling
- ✅ AI powered responses (Groq)
- ✅ Natural voice (Polly.Joanna)
- ✅ Multi-turn conversation
- ✅ Twilio integration
- ✅ Ngrok tunnel support

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Groq (LLaMA 3.3) | AI Brain |
| Twilio | Phone Calls |
| Flask | Web Server |
| Ngrok | Tunnel |
| Edge TTS | Voice |
| Python | Language |

---

## Setup

### Install Requirements
pip install groq twilio flask python-dotenv edge-tts playsound openai-whisper

### Environment Variables
Create .env file:
GROQ_API_KEY=your_key
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_number
NGROK_AUTH_TOKEN=your_token

### Run
Step 1: ngrok http 5000
Step 2: python call_agent.py
Step 3: python test_call.py

---

## Business
HamoraAgents — AI Call Agents & Chatbots
📧 hamoraagents@gmail.com