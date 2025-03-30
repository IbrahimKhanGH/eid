from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import openai
import anthropic
import os
from dotenv import load_dotenv
import threading
import time

# Load environment variables
load_dotenv()

# Initialize AI clients
openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
anthropic_client = anthropic.Client(api_key=os.getenv('ANTHROPIC_API_KEY'))

app = Flask(__name__)
CORS(app)

def get_openai_response(question):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for a Kahoot trivia game. Provide ONLY the letter of the correct answer (A, B, C, or D) followed by a brief explanation. Be extremely concise."},
                {"role": "user", "content": f"Question: {question}"}
            ],
            max_tokens=50
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def get_anthropic_response(question):
    try:
        response = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=50,
            messages=[
                {"role": "user", "content": f"Answer this Kahoot question with ONLY the letter (A, B, C, or D) and a brief explanation: {question}"}
            ]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

def get_perplexity_response(question):
    try:
        # Note: Implement Perplexity API call here
        return "Perplexity API not implemented"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get('question', '')
    
    # Get responses from all AIs in parallel
    responses = {
        'openai': get_openai_response(question),
        'anthropic': get_anthropic_response(question),
        'perplexity': get_perplexity_response(question)
    }
    
    return jsonify(responses)

# For local development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 