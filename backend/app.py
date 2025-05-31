from flask import Flask, request, jsonify, json
from flask_cors import CORS
from datetime import datetime
import os
import uuid
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("Gemini API key missing. Set GEMINI_API_KEY in your .env file.")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory storage
memory_storage = {}

@app.route('/upload', methods=['POST'])
def upload():
    format_type = None
    intent = None
    extracted_data = {}
    thread_id = str(uuid.uuid4())  # Unique ID for each session/thread

    if 'fileInput' in request.files:
        file = request.files['fileInput']
        filename = file.filename
        if filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'})
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(UPLOAD_FOLDER, f"{timestamp}_{filename}")
        file.save(save_path)
        print(f"File saved to {save_path}")
        content = extract_text_from_pdf(save_path)
        source_type = "File"
        source = filename
    elif 'textInput' in request.form:
        content = request.form['textInput']
        source_type = "Text"
        source = "TextInput"
    else:
        return jsonify({'status': 'error', 'message': 'No input provided'})

    format_type, intent = classify_intent(content)
    print(f"Detected Format: {format_type}, Intent: {intent}")

    if format_type == "JSON":
        extracted_data = json_agent(content)
    elif format_type == "Email":
        extracted_data = email_agent(content)
    elif format_type == "PDF":
        extracted_data = pdf_agent(content)
    else:
        extracted_data = {"error": "Unsupported format"}

    # Store memory in dictionary
    memory_storage[thread_id] = {
        'source': source,
        'type': source_type,
        'timestamp': datetime.now().isoformat(),
        'extracted_values': extracted_data
    }

    return jsonify({
        'status': 'success',
        'format': format_type,
        'intent': intent,
        'thread_id': thread_id,
        'extracted_data': extracted_data
    })

@app.route('/get_all', methods=['GET'])
def get_all():
    return jsonify(memory_storage)


def extract_text_from_pdf(file_path):
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except:
        return "Could not extract text from PDF."

def classify_intent(content):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "Classify the following content (format should be PDF, Email, JSON or other. "
            "If content is both PDF and Email, classify it as Email. If content is in JSON format, it will be JSON only) "
            "and reply ONLY with this JSON format:\n"
            '{"format": X, "intent": Y}\n'
            "No explanations or extra text.\n\n"
            f"Content:\n{content}"
        )
        response = model.generate_content(prompt)
        reply = response.text.strip()
        print(f"Gemini raw reply:\n{reply}")
        if reply.startswith("```"):
            reply = reply.strip("```")
            if reply.lower().startswith("json"):
                reply = reply[4:]
        reply = reply.strip()
        print(f"Cleaned JSON reply:\n{reply}")
        parsed = json.loads(reply)
        return parsed.get("format", "Unknown"), parsed.get("intent", "Unknown")
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Unknown", "Unknown"

def json_agent(content):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "Parse the following JSON content and check if it contains these required fields: 'id', 'name', 'amount'. "
            "Reply only with this JSON format:\n"
            '{"parsed": {...}, "missing_fields": [...]}'
            "where 'parsed' is the parsed JSON and 'missing_fields' is a list of missing required fields.\n\n"
            f"JSON Content:\n{content}"
        )
        response = model.generate_content(prompt)
        reply = response.text.strip()
        print(f"Gemini JSON Agent raw reply:\n{reply}")
        if reply.startswith("```"):
            reply = reply.strip("```")
            if reply.lower().startswith("json"):
                reply = reply[4:]
        reply = reply.strip()
        return json.loads(reply)
    except Exception as e:
        print(f"Gemini JSON Agent Error: {e}")
        return {"error": str(e)}

def email_agent(content):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "Extract the following fields from the given email content:\n"
            "- sender (who sent the email)\n"
            "- subject (subject of the email)\n"
            "- urgency (High if the email is urgent, else Normal)\n"
            "Reply only with JSON in this format:\n"
            '{"sender": "name", "subject": "subject line", "urgency": "High"}\n'
            f"Email Content:\n{content}"
        )
        response = model.generate_content(prompt)
        reply = response.text.strip()
        print(f"Gemini Email raw reply:\n{reply}")
        if reply.startswith("```"):
            reply = reply.strip("```")
            if reply.lower().startswith("json"):
                reply = reply[4:]
        reply = reply.strip()
        return json.loads(reply)
    except Exception as e:
        print(f"Gemini Email Agent Error: {e}")
        return {"sender": "Unknown", "subject": "No Subject", "urgency": "Normal"}

def pdf_agent(content):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "Summarize the following PDF content into approximately 200 characters. "
            "Reply only with the summary text, no explanations or extra formatting.\n\n"
            f"PDF Content:\n{content}"
        )
        response = model.generate_content(prompt)
        summary = response.text.strip()
        print(f"Gemini PDF summary:\n{summary}")
        if summary.startswith("```"):
            summary = summary.strip("```")
        return {"content_summary": summary[:200]}
    except Exception as e:
        print(f"Gemini PDF Agent Error: {e}")
        return {"content_summary": content[:200]}

if __name__ == '__main__':
    app.run(debug=True, port=5000)