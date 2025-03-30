import speech_recognition as sr
import tkinter as tk
from tkinter import ttk
import openai
import anthropic
import os
from dotenv import load_dotenv
import threading
from queue import Queue
import time

# Load environment variables
load_dotenv()

# Initialize AI clients
openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
anthropic_client = anthropic.Client(api_key=os.getenv('ANTHROPIC_API_KEY'))

class TriviaHelper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kahoot Trivia Helper")
        self.root.geometry("800x600")
        
        # Create and configure the main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create widgets
        self.status_label = ttk.Label(self.main_frame, text="Status: Ready", font=('Arial', 12))
        self.status_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        self.question_text = tk.Text(self.main_frame, height=3, width=70, font=('Arial', 12))
        self.question_text.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Create frames for each AI response
        self.ai_frames = []
        self.ai_labels = []
        self.ai_texts = []
        
        for i in range(3):
            frame = ttk.LabelFrame(self.main_frame, text=f"AI {i+1} Response", padding="5")
            frame.grid(row=2+i, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
            self.ai_frames.append(frame)
            
            text = tk.Text(frame, height=4, width=70, font=('Arial', 11))
            text.pack(fill=tk.BOTH, expand=True)
            self.ai_texts.append(text)
        
        self.listen_button = ttk.Button(
            self.main_frame, 
            text="🎤 Click & Speak Question", 
            command=self.start_listening,
            style='Accent.TButton'
        )
        self.listen_button.grid(row=5, column=0, columnspan=2, pady=20)
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.answer_queue = Queue()
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Create custom style
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 12, 'bold'))
        
    def start_listening(self):
        if self.is_listening:
            self.is_listening = False
            self.listen_button.config(text="🎤 Click & Speak Question")
            self.status_label.config(text="Status: Ready")
        else:
            self.is_listening = True
            self.listen_button.config(text="⏹ Stop Listening")
            self.status_label.config(text="Status: Listening...")
            threading.Thread(target=self.listen_for_question, daemon=True).start()
    
    def listen_for_question(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)  # Reduced noise adjustment time
                audio = self.recognizer.listen(source, timeout=5)  # Added timeout
                
            self.status_label.config(text="Status: Processing...")
            self.root.update()
            
            # Convert speech to text
            text = self.recognizer.recognize_google(audio)
            self.question_text.delete(1.0, tk.END)
            self.question_text.insert(tk.END, text)
            
            # Start parallel AI processing
            threads = [
                threading.Thread(target=self.get_openai_response, args=(text, 0), daemon=True),
                threading.Thread(target=self.get_anthropic_response, args=(text, 1), daemon=True),
                threading.Thread(target=self.get_perplexity_response, args=(text, 2), daemon=True)
            ]
            
            for thread in threads:
                thread.start()
            
            # Reset listening state
            self.is_listening = False
            self.listen_button.config(text="🎤 Click & Speak Question")
            self.status_label.config(text="Status: Ready")
            
        except Exception as e:
            self.status_label.config(text=f"Status: Error - {str(e)}")
            self.is_listening = False
            self.listen_button.config(text="🎤 Click & Speak Question")
    
    def get_openai_response(self, question, index):
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for a Kahoot trivia game. Provide ONLY the letter of the correct answer (A, B, C, or D) followed by a brief explanation. Be extremely concise."},
                    {"role": "user", "content": f"Question: {question}"}
                ],
                max_tokens=50  # Limit response length
            )
            answer = response.choices[0].message.content
            self.ai_texts[index].delete(1.0, tk.END)
            self.ai_texts[index].insert(tk.END, answer)
        except Exception as e:
            self.ai_texts[index].delete(1.0, tk.END)
            self.ai_texts[index].insert(tk.END, f"Error: {str(e)}")
    
    def get_anthropic_response(self, question, index):
        try:
            response = anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=50,  # Limit response length
                messages=[
                    {"role": "user", "content": f"Answer this Kahoot question with ONLY the letter (A, B, C, or D) and a brief explanation: {question}"}
                ]
            )
            answer = response.content[0].text
            self.ai_texts[index].delete(1.0, tk.END)
            self.ai_texts[index].insert(tk.END, answer)
        except Exception as e:
            self.ai_texts[index].delete(1.0, tk.END)
            self.ai_texts[index].insert(tk.END, f"Error: {str(e)}")
    
    def get_perplexity_response(self, question, index):
        try:
            # Note: Perplexity API implementation would go here
            # You'll need to add your Perplexity API key to .env
            self.ai_texts[index].delete(1.0, tk.END)
            self.ai_texts[index].insert(tk.END, "Perplexity API not implemented")
        except Exception as e:
            self.ai_texts[index].delete(1.0, tk.END)
            self.ai_texts[index].insert(tk.END, f"Error: {str(e)}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TriviaHelper()
    app.run() 