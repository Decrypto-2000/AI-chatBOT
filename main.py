import os
from openai import OpenAI
import tkinter as tk
import threading
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print("API key loaded:", bool(api_key))

client = OpenAI(api_key=api_key)

# Initialize Text-to-Speech
engine = pyttsx3.init()

# Chat history to maintain context
chat_history = [
    {"role": "system", "content": "You are a helpful assistant."}
]

# Function to send message to OpenAI and get response
def ask_openai_stream(prompt, display_callback, speak_callback):
    chat_history.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=chat_history,
        stream=True
    )

    full_response = ""
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response += content
            display_callback(content)

    chat_history.append({"role": "assistant", "content": full_response})
    speak_callback(full_response)

# Function to speak the response
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Voice input
def voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        status_label.config(text="Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        input_entry.delete(0, tk.END)
        input_entry.insert(0, text)
        send_message()
    except sr.UnknownValueError:
        status_label.config(text="Sorry, I didn't understand.")
    except sr.RequestError:
        status_label.config(text="Voice recognition service error.")

# GUI setup
def send_message():
    user_input = input_entry.get()
    if not user_input:
        return
    chat_log.insert(tk.END, f"You: {user_input}\n")
    input_entry.delete(0, tk.END)
    status_label.config(text="Thinking...")

    def display_typing(content):
        chat_log.insert(tk.END, content)
        chat_log.see(tk.END)

    def run():
        global typing_animation_running
        typing_animation_running = True
        start_typing_animation()

        ask_openai_stream(
            user_input,
            display_callback=display_typing,
            speak_callback=speak
        )

        stop_typing_animation()
        chat_log.insert(tk.END, "\n")
        status_label.config(text="Ready")

    threading.Thread(target=run).start()
# Main window
app = tk.Tk()
app.title("AI Voice Chat Bot")
app.geometry("500x600")

chat_log = tk.Text(app, wrap=tk.WORD, height=25, width=60)
chat_log.pack(padx=10, pady=10)

input_frame = tk.Frame(app)
input_frame.pack(pady=5)

input_entry = tk.Entry(input_frame, width=40, font=("Arial", 12))
input_entry.pack(side=tk.LEFT, padx=5)

send_button = tk.Button(input_frame, text="Send", command=send_message)
send_button.pack(side=tk.LEFT)

mic_button = tk.Button(input_frame, text="🎤 Speak", command=lambda: threading.Thread(target=voice_input).start())
mic_button.pack(side=tk.LEFT, padx=5)

status_label = tk.Label(app, text="Ready", fg="green")
status_label.pack(pady=5)

typing_label = tk.Label(app, text="", font=("Arial", 10), fg="gray")
typing_label.pack(pady=5)


typing_animation_running = False

def start_typing_animation():
    def animate(i=0):
        if typing_animation_running:
            dots = "." * (i % 4)
            typing_label.config(text=f"AI is typing{dots}")
            app.after(500, animate, i + 1)
    animate()

def stop_typing_animation():
    global typing_animation_running
    typing_animation_running = False
    typing_label.config(text="")


app.mainloop()
