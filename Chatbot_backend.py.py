

from pydantic import BaseModel
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import webbrowser  # For opening the web browser and searching Google or YouTube
import pyautogui  # To control the mouse and keyboard
import time

# Configure the Google Gemini API key (make sure to replace with your actual key)
genai.configure(api_key='AIzaSyDhd9xZ_bDCWzTf_XlJpOfvF_Bsa8xGbBk')

# Initialize the text-to-speech engine
engine = pyttsx3.init('sapi5')

# Set the speech rate (increase for faster speed)
rate = engine.getProperty('rate')  # Get the current rate
engine.setProperty('rate', rate + 40)  # Increase the rate by 40 (adjust this value as needed)

# Create FastAPI app
app = FastAPI()

# Enable CORS (allow requests from any origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"," http://127.0.0.1:5000","http://localhost:8000","http://localhost:8080", "file://"],  # Allows all origins; adjust if you want to limit
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

class TextInput(BaseModel):
    input: str

# Function to speak
def speak(text):
    print(f"Speaking: {text}")  # Print what is being spoken
    engine.say(text)
    engine.runAndWait()

# Function to listen to voice commands
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that. Say again please.")
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            speak("Could not request results from Google Speech Recognition service.")
            print("Could not request results from Google Speech Recognition service.")
            return None

# Function to get a response from Gemini API (Google's Generative AI)
def get_response(prompt):
    # Add context or instructions for the model
    context = (
        "You are a helpful AI assistant. Always provide concise, accurate, and informative responses. "
        "Generate just concise answer and according to the user's prompt"
        "If the user asks for technical details, provide them step-by-step in an easy-to-understand way. "
        "Here is the user's request:"
    )
    
    # Combine the context with the user's prompt
    full_prompt = f"{context}\n\n{prompt}"
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(full_prompt)
    print(response.text)
    return response.text

def search_google(query):
    search_query = '+'.join(query.split())  # Replace spaces with '+' for a proper URL
    url = f"https://www.google.com/search?q={search_query}"
    webbrowser.open(url)
    speak(f"Searching for {query} on Google.")

# Function to perform a YouTube search
def search_youtube(query):
    search_query = '+'.join(query.split())  # Replace spaces with '+' for a proper URL
    url = f"https://www.youtube.com/results?search_query={search_query}"
    webbrowser.open(url)
    speak(f"Searching for {query} on YouTube.")

# Function to click on the first video result (automating the cursor)
def play_youtube_video(query):
    search_query = '+'.join(query.split())  # Replace spaces with '+' for a proper URL
    url = f"https://www.youtube.com/results?search_query={search_query}"
    webbrowser.open(url)
    speak(f"Searching for {query} on YouTube.")
    
    # Wait for the YouTube page to load
    time.sleep(5)

    # Automate the mouse to click on the first video
    try:
        pyautogui.moveTo(600, 400)  # Coordinates of the first video (you may need to adjust these)
        pyautogui.click()
        speak(f"Now playing {query}.")
    except Exception as e:
        speak(f"Could not click the video. Error: {str(e)}")

# Function to control the cursor and perform tasks
def automate_cursor(command):
    if "scroll down" in command:
        pyautogui.scroll(-100)
        speak("Scrolling down.")
    elif "scroll up" in command:
        pyautogui.scroll(100)
        speak("Scrolling up.")
    elif "click" in command:
        pyautogui.click()
        speak("Clicking.")
    elif "move" in command:
        pyautogui.moveTo(100, 100)
        speak("Moving the cursor to the top-left corner.")
    # You can expand this with more commands to control the cursor.

# FastAPI endpoint to handle voice input and speaking
@app.post("/process_voice/")
async def process_voice():
    speak("Hello, I'm You AI Assistant. How can I help You?")
    command = await asyncio.to_thread(listen)  # Use asyncio to run listen in a separate thread
    if command:
        command = command.lower()
        
        # If the command is to quit
        if "exit" in command or "quit" in command:
            speak("Goodbye!")
            return JSONResponse(content={"response": "Goodbye!"})
        elif "play" in command or "play song" in command:
            play_youtube_video(command)
            return JSONResponse(content={"response": "Processing your query"})
        elif "youtube" in command or "search on youtube" in command:
            search_youtube(command)
            return JSONResponse(content={"response": "Processing your query"})
        elif "search" in command or "search on google" in command or "search google" in command:
            search_google(command)
            return JSONResponse(content={"response": "Processing your query"})
        
        # Process normal AI responses
        response = get_response(command)
        speak(response)
        return JSONResponse(content={"response": response, "command" : command})

@app.post("/manual_input/")
async def manual_input(text: TextInput):
    parsedData = text.input
    
    if "play" in parsedData or "play song" in parsedData:
        play_youtube_video(parsedData)
        return JSONResponse(content={"response": f"Processing your query {parsedData}"})
    elif "youtube" in parsedData or "search on youtube" in parsedData:
        search_youtube(parsedData)
        return JSONResponse(content={"response": f"Processing your query {parsedData}"})
    elif "search" in parsedData or "search on google" in parsedData or "search google" in parsedData:
        search_google(parsedData)
        return JSONResponse(content={"response": f"Processing your query {parsedData}"})
    
    response = get_response(parsedData)  # Process the input via the AI model
    # speak(response)  # Speak out the response
    return JSONResponse(content={"response": response})

# FastAPI endpoint to speak a text directly
@app.post("/speak/")
async def speak_text(text: str):
    speak(text)
    return JSONResponse(content={"response": f"Speaking: {text}"})

# Function to run the FastAPI server
def run_server():
    uvicorn.run(app, host="0.0.0.0", port=5000)

# Start the FastAPI server inside the Python script
if __name__ == "__main__":
    run_server()
