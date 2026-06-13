from groq import Groq
from dotenv import load_dotenv
import os
import edge_tts
import asyncio
from playsound import playsound
import tempfile
import re
import json

# API Key Load
load_dotenv()

# Pharmacy Data Load
with open('medicines.json', 'r') as f:
    pharmacy_data = json.load(f)

# Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Clean Text
def clean_text(text):
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'#+', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    return text.strip()

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

# Welcome Message
welcome = f"Hello! I am Zara, your AI assistant from {pharmacy_data['pharmacy_name']}. How can I help you today?"
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
            bye = "Thank you for calling. Have a great day!"
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