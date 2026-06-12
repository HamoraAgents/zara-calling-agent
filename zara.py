from groq import Groq
from dotenv import load_dotenv
import os
import edge_tts
import asyncio
from playsound import playsound
import tempfile
import re

# API Key Load
load_dotenv()

# Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Clean Text Function
def clean_text(text):
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'#+', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = text.strip()
    return text

# Voice Function
async def speak(text):
    try:
        text = clean_text(text)
        if not text:
            return

        voice = "en-US-JennyNeural"
        communicate = edge_tts.Communicate(text, voice)
        temp_file = tempfile.mktemp(suffix=".mp3")
        await communicate.save(temp_file)
        playsound(temp_file)

        try:
            os.unlink(temp_file)
        except:
            pass

    except Exception as e:
        print(f"Voice error: {e}")

# Zara Ki Identity
messages = [
    {
        "role": "system",
        "content": """You are Zara, a professional AI voice assistant from HamoraAgents.

STRICT RULES:
- ALWAYS reply in English only
- NEVER use Urdu or any other script
- Keep responses short — max 2 to 3 sentences
- Be natural, friendly and professional
- No asterisk or special characters in responses
- Give direct answers — no extra filler words

IDENTITY:
- Your name is Zara
- You are AI voice assistant from HamoraAgents
- You help businesses automate their customer calls"""
    }
]

# Welcome Message
welcome = "Hello! I am Zara, your AI assistant from HamoraAgents. How can I help you today?"
print(f"\nZara: {welcome}")
print("(Type 'exit' to quit)\n")
print("-" * 45)
asyncio.run(speak(welcome))

# Main Loop
while True:
    try:
        user_input = input("\nYou: ").strip()

        # Exit
        if user_input.lower() in ["exit", "quit", "bye"]:
            bye = "Goodbye! Have a wonderful day!"
            print(f"Zara: {bye}")
            asyncio.run(speak(bye))
            break

        # Empty Input
        if not user_input:
            continue

        # History Mein Add
        messages.append({
            "role": "user",
            "content": user_input
        })

        # Groq Se Jawab
        chat = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=120,
            temperature=0.7
        )

        response = chat.choices[0].message.content
        response = clean_text(response)

        # History Update
        messages.append({
            "role": "assistant",
            "content": response
        })

        # Print Aur Bolo
        print(f"\nZara: {response}")
        print("-" * 45)
        asyncio.run(speak(response))

    except KeyboardInterrupt:
        print("\nZara: Goodbye!")
        break
    except Exception as e:
        print(f"\nError: {e}")
        print("Please try again!")