import speech_recognition as sr
import os
import webbrowser
import datetime
import random
import win32com.client
import requests
import google.generativeai as genai

# API Keys
NEWS_API_KEY = " "
WEATHER_API_KEY = " "
GEMINI_API_KEY = " "

# Initialize Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize voice engine
speaker = win32com.client.Dispatch("SAPI.SpVoice")

def say(text):
    speaker.Speak(text)

def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source)
            return recognizer.recognize_google(audio, language="en-US").lower()
        except Exception as e:
            return "Sorry, I couldn't understand that."

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        articles = data.get("articles", [])[:5]
        if articles:
            headlines = "\n".join([f"News {i+1}: {article.get('title', 'No title available')}"
                                   for i, article in enumerate(articles)])
            return f"Here are the top news headlines:\n{headlines}"
        else:
            return "Sorry, I couldn't fetch the news."
    except Exception as e:
        return "An error occurred while fetching the news."

def get_weather(city="Kolkata"):
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no"
    try:
        response = requests.get(url)
        data = response.json()
        if "current" in data:
            temp = data["current"]["temp_c"]
            condition = data["current"]["condition"]["text"]
            return f"The current temperature in {city} is {temp}°C with {condition}."
        else:
            return "Sorry, I couldn't fetch the weather."
    except Exception as e:
        return "An error occurred while fetching the weather."

def execute_command(query):
    sites = {
        "youtube": "https://www.youtube.com",
        "wikipedia": "https://www.wikipedia.com",
        "google": "https://www.google.com",
        "gmail": "https://mail.google.com",
        "whatsapp": "https://web.whatsapp.com"
    }

    # Check for site-opening commands
    for site, url in sites.items():
        if f"open {site}" in query:
            webbrowser.open(url)
            return f"Opening {site}."

    if "play music" in query:
        os.system("start \"\" \"C:\\Users\\Dev\\Music\\Take You Dancing.mp3\"")
        return "Playing music."

    elif "the time" in query:
        return f"The time is {datetime.datetime.now().strftime('%H:%M')}"

    elif "news" in query:
        return get_news()

    elif "weather" in query:
        words = query.split()
        if "in" in words:
            city = " ".join(words[words.index("in") + 1:])
        else:
            city = "Kolkata"
        return get_weather(city)

    elif "search for" in query:
        search_query = query.replace("search for", "").strip()
        if search_query:
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
            return f"Searching Google for {search_query}."
        else:
            return "I didn't understand what to search for."

    elif "stop" in query or "exit" in query:
        return "Goodbye!"


    else:

        try:
            model = genai.GenerativeModel("gemini-1.5-pro-latest")
            response = model.generate_content(query)

            if response and response.text:
                return response.text  # No truncation here

            else:
                return "Couldn't get a response."
        except Exception as e:
            return "An error occurred with Gemini AI."

