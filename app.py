import os
from flask import Flask, render_template, request, jsonify
from groq import Groq
import PyPDF2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Groq client
# The client automatically looks for the GROQ_API_KEY environment variable
api_key = os.environ.get("GROQ_API_KEY")
client = None
if api_key and api_key != "your_groq_api_key_here":
    client = Groq(api_key=api_key)

# Global variable to store resume text
resume_text = ""

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

# Load resume on startup
RESUME_PATH = r"c:\Users\rsmd2\Downloads\smruti's resume (1).pdf"
resume_text = extract_text_from_pdf(RESUME_PATH)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    if not client:
        return jsonify({"error": "Groq API key is missing. Please set GROQ_API_KEY in the .env file."}), 500

    data = request.json
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    if not resume_text:
        return jsonify({"error": "Resume text could not be loaded. Please check the PDF path."}), 500

    try:
        # System prompt specifying the persona and providing the context
        system_prompt = f"""You are an AI portfolio assistant for Smruti. 
Your primary goal is to answer questions about Smruti's education, skills, projects, and achievements based EXACTLY on the provided resume details.
Do not invent or hallucinate any information.
Be professional, concise, and helpful. If someone asks a question that cannot be answered using the resume text, politely inform them that you do not have that information.
Here is the text extracted from Smruti's resume:

---------------------
{resume_text}
---------------------
"""

        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            model="llama-3.1-8b-instant", # Fast and capable open source model on Groq
            temperature=0.2, # Low temperature for more factual responses
            max_tokens=1024,
        )

        bot_reply = chat_completion.choices[0].message.content
        return jsonify({"reply": bot_reply})

    except Exception as e:
        print(f"Error during Groq API call: {e}")
        return jsonify({"error": "An error occurred while communicating with the AI. Please try again later."}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
