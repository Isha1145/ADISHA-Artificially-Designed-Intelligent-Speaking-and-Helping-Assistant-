import speech_recognition as sr
import os
import webbrowser
import google.generativeai as genai
from config import apikey
import datetime
import pywhatkit
from gtts import gTTS
from playsound import playsound
from googletrans import Translator
import uuid

# Gemini API
genai.configure(api_key=apikey)
translator = Translator()

# Global variables
chatStr = ""
current_language = "en"  # Options: 'en', 'hi', 'mr'
language_name = {"en": "English", "hi": "Hindi", "mr": "Marathi"}

# Speak function using gTTS
def say(text, lang='en'):
    print("ADISHA:", text)
    tts = gTTS(text=text, lang=lang)
    filename = f"temp_{uuid.uuid4()}.mp3"
    tts.save(filename)
    playsound(filename)
    os.remove(filename)

# Gemini chat
def chat(query):
    global chatStr
    chatStr += f"User: {query}\nADISHA: "

    try:
        model = genai.GenerativeModel("models/gemini-1.5-pro")
        response = model.generate_content(query)
        reply = response.text
        if current_language != 'en':
            reply = translator.translate(reply, dest=current_language).text
        say(reply, lang=current_language)
        chatStr += f"{reply}\n"
        return reply
    except Exception as e:
        say("Sorry, there was an error with Gemini.", lang=current_language)
        print("Gemini Error:", e)
        return "Error"

# Save AI response to file
def ai(prompt):
    text = f"Gemini response for Prompt: {prompt}\n*\n\n"
    try:
        model = genai.GenerativeModel("models/gemini-1.5-pro")
        response = model.generate_content(prompt)
        result = response.text
        text += result
        if not os.path.exists("Gemini"):
            os.mkdir("Gemini")
        filename = f"Gemini/{'_'.join(prompt.split()[:5])}.txt"
        with open(filename, "w") as f:
            f.write(text)
        say("Response saved successfully.", lang=current_language)
    except Exception as e:
        say("Failed to get response from Gemini.", lang=current_language)
        print("Gemini Error:", e)

# Take voice command
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        query = r.recognize_google(audio, language=f"{current_language}-IN")
        print("User said:", query)
        return query.lower()
    except sr.UnknownValueError:
        say("Sorry, I didn't catch that. Please try again.", lang=current_language)
        return ""
    except sr.RequestError as e:
        say("Could not request results. Please check your internet.", lang=current_language)
        print("RequestError:", e)
        return ""

# Main program
if _name_ == '_main_':
    print("Welcome to ADISHA A.I")
    say("ADISHA A.I. Activated", lang=current_language)

    while True:
        query = takeCommand()

        if not query:
            continue

        # Language switching
        if "say in hindi" in query or "हिंदी मे बोल" in query:
            current_language = "hi"
            say("अब मैं हिंदी में बोलूँगी।", lang="hi")
            continue
        elif "say in marathi" in query or "मराठी बोल" in query:
            current_language = "mr"
            say("आता मी मराठीत बोलेन.", lang="mr")
            continue
        elif "say in english" in query or "अंग्रेजी में बात करो" in query:
            current_language = "en"
            say("I will now speak in English.", lang="en")
            continue

        # Jokes
        if "tell me a joke" in query:
            joke = "Why don't scientists trust atoms? Because they make up everything!"
            if current_language != "en":
                joke = translator.translate(joke, dest=current_language).text
            say(joke, lang=current_language)
            continue

        # Website handling
        sites = [["youtube", "https://www.youtube.com"],
                 ["wikipedia", "https://www.wikipedia.org"],
                 ["google", "https://www.google.com"],
                 ["spotify", "https://open.spotify.com"]]

        for site in sites:
            if f"open {site[0]}" in query:
                say(f"Opening {site[0]}...", lang=current_language)
                webbrowser.open(site[1])
                break

        # YouTube play using pywhatkit
        if "play on youtube" in query:
            song = query.replace("play on youtube", "").strip()
            say(f"Playing {song} on YouTube.", lang=current_language)
            pywhatkit.playonyt(song)
            continue

        # Time
        elif "the time" in query or "kitna baj gaya" in query:
            now = datetime.datetime.now()
            current_time = f"The time is {now.strftime('%H')} hours and {now.strftime('%M')} minutes."
            if current_language != "en":
                current_time = translator.translate(current_time, dest=current_language).text
            say(current_time, lang=current_language)

        # Open Chrome
        elif "open chrome" in query:
            os.system("google-chrome &")
            say("Opening Chrome.", lang=current_language)

        # Open VS Code
        elif "open vs code" in query:
            os.system("code &")
            say("Opening Visual Studio Code.", lang=current_language)

        # Custom AI
        elif "using artificial intelligence" in query:
            ai(prompt=query)

        # Exit
        elif "adisha quit" in query or "exit" in query:
            say("Goodbye sir.", lang=current_language)
            break

        # Reset Chat
        elif "reset chat" in query:
            chatStr = ""
            say("Chat history reset.", lang=current_language)

        # Default: Use Gemini chat
        else:
            chat(query)
