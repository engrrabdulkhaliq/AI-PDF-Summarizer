from flask import Flask, render_template, request, jsonify, send_file, session
import os
import io
import PyPDF2
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
from dotenv import load_dotenv
from groq import Groq
import json
from datetime import datetime
import hashlib
import secrets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("❌ GROQ_API_KEY not found in .env")

client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB
app.config["UPLOAD_FOLDER"] = "uploads"

ALLOWED_EXTENSIONS = {"pdf"}
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

chat_sessions = {}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_file, use_ocr=False):
    try:
        text = ""
        page_count = 0
        
        pdf_bytes = pdf_file.read()
        pdf_file.seek(0)
        
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        page_count = len(reader.pages)
        
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text and page_text.strip():
                text += page_text + "\n"
        
        if not text.strip() and use_ocr:
            try:
                images = convert_from_bytes(pdf_bytes, first_page=1, last_page=min(10, page_count))
                for img in images:
                    text += pytesseract.image_to_string(img) + "\n"
            except Exception as e:
                print(f"OCR failed: {str(e)}")
        
        return text.strip(), page_count
    except Exception as e:
        raise ValueError(f"Error reading PDF: {str(e)}")

def chunk_text(text, max_chars=4000):
    chunks = []
    current_chunk = ""
    
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        if len(current_chunk) + len(para) <= max_chars:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def get_ai_response(system_prompt, user_prompt, max_tokens=1500):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

def translate_text(text, target_language):
    if target_language == "english":
        return text
    
    language_map = {
        "spanish": "Spanish",
        "chinese": "Chinese (Simplified)",
        "hindi": "Hindi",
        "french": "French",
        "german": "German",
        "japanese": "Japanese",
        "korean": "Korean",
        "arabic": "Arabic",
        "urdu": "Urdu",
        "portuguese": "Portuguese"
    }
    
    system_prompt = f"You are a professional translator. Translate the following text to {language_map.get(target_language, target_language)} while maintaining the original meaning and tone."
    
    return get_ai_response(system_prompt, f"Translate this text:\n\n{text}")

def summarize_text(text, audience="general", length="medium", language="english"):
    length_map = {
        "short": "in 3–5 concise sentences",
        "medium": "in 2–3 clear paragraphs",
        "detailed": "in 4–5 detailed paragraphs with key insights"
    }

    audience_map = {
        "general": "for a general audience using clear language",
        "ceo": "for executives focusing on strategic insights and business impact",
        "lawyer": "for legal professionals highlighting clauses, risks, and compliance",
        "researcher": "for researchers emphasizing methodology, findings, and data",
        "student": "for students using simple, educational language"
    }

    system_prompt = "You are an expert document analyst. Create comprehensive, accurate summaries that capture essential information."

    user_prompt = f"""
    Summarize this document {length_map[length]} {audience_map[audience]}:

    {text}
    
    Provide a well-structured, coherent summary with key insights.
    """

    summary = get_ai_response(system_prompt, user_prompt, max_tokens=2000)
    
    if language != "english":
        summary = translate_text(summary, language)
    
    return summary

def extract_key_points(text, num_points=7):
    system_prompt = "You are an expert at identifying critical insights and key points from documents."
    
    user_prompt = f"""
    Extract {num_points} key points from this document.
    Format as a clear numbered list with brief explanations.
    
    Document:
    {text[:5000]}
    """
    
    return get_ai_response(system_prompt, user_prompt)

def generate_mindmap_data(text):
    system_prompt = "You are an expert at creating structured mind maps from documents."
    
    user_prompt = f"""
    Analyze this document and create a hierarchical mind map structure.
    Return ONLY valid JSON in this exact format:
    {{
        "central": "Main Topic",
        "branches": [
            {{"name": "Branch 1", "subbranches": ["Detail 1", "Detail 2"]}},
            {{"name": "Branch 2", "subbranches": ["Detail 1", "Detail 2"]}}
        ]
    }}
    
    Document (first 3000 chars):
    {text[:3000]}
    """
    
    response = get_ai_response(system_prompt, user_prompt)
    
    try:
        response = response.strip()
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        
        return json.loads(response)
    except:
        return {
            "central": "Document Analysis",
            "branches": [
                {"name": "Main Points", "subbranches": ["Point 1", "Point 2"]},
                {"name": "Key Insights", "subbranches": ["Insight 1", "Insight 2"]}
            ]
        }

def chat_with_document(document_text, question, chat_history=[]):
    system_prompt = f"""You are an AI assistant helping users understand a document. 
    Answer questions accurately based on the document content.
    
    Document content:
    {document_text[:6000]}
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history[-5:]:
        messages.append({"role": "user", "content": msg["question"]})
        messages.append({"role": "assistant", "content": msg["answer"]})
    messages.append({"role": "user", "content": question})
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.6,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    audience = request.form.get("audience", "general")
    length = request.form.get("summary_length", "medium")
    language = request.form.get("language", "english")
    include_key_points = request.form.get("include_key_points", "false") == "true"
    include_mindmap = request.form.get("include_mindmap", "false") == "true"
    use_ocr = request.form.get("use_ocr", "false") == "true"

    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    try:
        text, page_count = extract_text_from_pdf(file, use_ocr)

        if not text:
            return jsonify({"error": "Could not extract text. Try enabling OCR for scanned PDFs."}), 400

        word_count = len(text.split())
        char_count = len(text)
        reading_time = max(1, round(word_count / 200))

        chunks = chunk_text(text)

        if len(chunks) > 1:
            partial_summaries = [summarize_text(chunk, audience, "short", "english") for chunk in chunks[:10]]
            combined = " ".join(partial_summaries)
            final_summary = summarize_text(combined, audience, length, language)
        else:
            final_summary = summarize_text(text, audience, length, language)

        key_points = extract_key_points(text) if include_key_points else None
        mindmap_data = generate_mindmap_data(text) if include_mindmap else None

        session_id = hashlib.md5(f"{file.filename}{datetime.now()}".encode()).hexdigest()
        chat_sessions[session_id] = {
            "text": text[:10000],
            "filename": file.filename,
            "created_at": datetime.now().isoformat()
        }
        
        current_time = datetime.now()
        sessions_to_delete = [
            sid for sid, data in chat_sessions.items()
            if (current_time - datetime.fromisoformat(data["created_at"])).seconds > 3600
        ]
        for sid in sessions_to_delete:
            del chat_sessions[sid]

        return jsonify({
            "success": True,
            "summary": final_summary,
            "key_points": key_points,
            "mindmap_data": mindmap_data,
            "session_id": session_id,
            "metadata": {
                "filename": file.filename,
                "char_count": char_count,
                "word_count": word_count,
                "page_count": page_count,
                "reading_time": reading_time,
                "audience": audience,
                "length": length,
                "language": language,
                "timestamp": datetime.now().isoformat()
            }
        })

    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    session_id = data.get("session_id")
    question = data.get("question", "").strip()
    
    if not session_id or session_id not in chat_sessions:
        return jsonify({"error": "Invalid session. Please upload a PDF first."}), 400
    
    if not question:
        return jsonify({"error": "Please enter a question"}), 400
    
    try:
        doc_data = chat_sessions[session_id]
        
        if "chat_history" not in doc_data:
            doc_data["chat_history"] = []
        
        answer = chat_with_document(doc_data["text"], question, doc_data["chat_history"])
        
        doc_data["chat_history"].append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })
        
        return jsonify({"success": True, "answer": answer, "question": question})
    
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

@app.route("/convert-to-text", methods=["POST"])
def convert_to_text():
    data = request.get_json()
    session_id = data.get("session_id")
    
    if not session_id or session_id not in chat_sessions:
        return jsonify({"error": "Invalid session"}), 400
    
    doc_data = chat_sessions[session_id]
    
    buffer = io.BytesIO()
    buffer.write(doc_data["text"].encode("utf-8"))
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{doc_data['filename']}_extracted.txt",
        mimetype="text/plain"
    )

@app.route("/download", methods=["POST"])
def download_summary():
    data = request.get_json()
    summary = data.get("summary", "")
    key_points = data.get("key_points", "")
    metadata = data.get("metadata", {})

    content = f"""{'='*60}
AI PDF SUMMARIZER - COMPLETE ANALYSIS
{'='*60}

Document: {metadata.get('filename', 'Unknown')}
Pages: {metadata.get('page_count', 'N/A')}
Words: {metadata.get('word_count', 'N/A')}
Reading Time: {metadata.get('reading_time', 'N/A')} minutes
Language: {metadata.get('language', 'english').title()}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*60}
SUMMARY ({metadata.get('length', 'medium').upper()})
{'='*60}

{summary}

"""

    if key_points:
        content += f"""
{'='*60}
KEY POINTS & INSIGHTS
{'='*60}

{key_points}
"""

    content += f"""

{'='*60}
Generated by AI PDF Summarizer
{'='*60}
"""

    buffer = io.BytesIO()
    buffer.write(content.encode("utf-8"))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mimetype="text/plain"
    )

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)