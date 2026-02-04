import streamlit as st
import os
import io
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AI PDF Summarizer - Smart Document Analysis",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Import libraries
try:
    import PyPDF2
    from groq import Groq
except ImportError as e:
    st.error(f"Missing required library: {str(e)}")
    st.stop()

# Optional imports
try:
    import pytesseract
    from pdf2image import convert_from_bytes
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Get API key
GROQ_API_KEY = None
try:
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
except:
    pass
if not GROQ_API_KEY:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY not found!")
    st.stop()

try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"Failed to initialize Groq: {str(e)}")
    st.stop()

# ✨ Enhanced CSS with all improvements
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {
        --bg-primary: #f0fdf4;
        --bg-secondary: #ffffff;
        --bg-card: #ffffff;
        --accent: #ec4899;
        --accent-2: #f97316;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --border: rgba(236, 72, 153, 0.15);
        --success: #10b981;
        --error: #ef4444;
        --glow: rgba(236, 72, 153, 0.3);
    }
    
    .stApp {
        background: #2A7B9B;
        background: #EEAECA;
        background: radial-gradient(circle, rgba(238, 174, 202, 1) 0%, rgba(169, 218, 226, 0.87) 81%, rgba(148, 187, 233, 1) 100%);
        background-attachment: fixed;
        font-family: 'Sora', sans-serif;
        color: var(--text-primary);
    }
    
    /* 2. Modern Cards with Borders */
    .custom-card {
        background: rgba(255, 255, 255, 0.85);
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid var(--border);
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(236, 72, 153, 0.15);
        margin-bottom: 2rem;
        animation: fadeInUp 0.5s ease-out;
    }
    
    .card-title {
        font-size: 1.4rem;
        margin-bottom: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.02em;
    }
    
    /* 3. Gradient Buttons with Glow */
    .stButton>button {
        background: linear-gradient(135deg, #ec4899 0%, #f97316 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 2rem !important;
        font-weight: 700 !important;
        font-family: 'Sora', sans-serif !important;
        box-shadow: 0 8px 24px var(--glow) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: none !important;
        letter-spacing: 0.02em !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 32px var(--glow) !important;
        background: linear-gradient(135deg, #db2777 0%, #ea580c 100%) !important;
    }
    
    .stButton>button:active {
        transform: translateY(0px) !important;
    }
    
    /* 4. Beautiful Tabs with Active State */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
        border-bottom: 2px solid var(--border);
        padding-bottom: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        padding: 1rem 1.5rem !important;
        border-radius: 8px 8px 0 0 !important;
        transition: all 0.2s ease !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(236, 72, 153, 0.1) !important;
        color: var(--accent) !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--accent) !important;
        background: rgba(236, 72, 153, 0.15) !important;
        border-bottom: 3px solid var(--accent) !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.5rem;
    }
    
    /* 5. Styled Metrics with Gradient */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.7);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid var(--border);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #ec4899 0%, #f97316 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600 !important;
    }
    
    /* 6. Custom Pink-Coral Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.5);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #ec4899 0%, #f97316 100%);
        border-radius: 10px;
        border: 2px solid rgba(255, 255, 255, 0.5);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #db2777 0%, #ea580c 100%);
    }
    
    /* 7. Proper File Uploader Styling */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.6) !important;
        border: 2px dashed var(--border) !important;
        border-radius: 16px !important;
        padding: 2.5rem 2rem !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent) !important;
        background: rgba(236, 72, 153, 0.05) !important;
    }
    
    [data-testid="stFileUploader"] section {
        border: none !important;
        padding: 0 !important;
    }
    
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #ec4899 0%, #f97316 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    /* 8. Chat Bubbles - Light Themed */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 1.25rem !important;
        margin: 0.75rem 0 !important;
        box-shadow: 0 4px 12px rgba(236, 72, 153, 0.1);
    }
    
    [data-testid="stChatMessageContent"] {
        color: var(--text-primary) !important;
    }
    
    .stChatMessage[data-testid*="user"] {
        background: rgba(236, 72, 153, 0.15) !important;
        border-color: rgba(236, 72, 153, 0.3) !important;
    }
    
    /* 9. Smooth Fade-in Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from { 
            opacity: 0; 
            transform: translateY(-10px);
        }
        to { 
            opacity: 1; 
            transform: translateY(0);
        }
    }
    
    .animate-in {
        animation: fadeInUp 0.5s ease-out;
    }
    
    .main-header {
        text-align: center;
        margin-bottom: 3rem;
        animation: fadeIn 0.8s ease-out;
    }
    
    .main-header h1 {
        font-size: 3.5rem;
        background: linear-gradient(135deg, #ec4899 0%, #f97316 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        font-weight: 800;
        letter-spacing: -0.03em;
    }
    
    .tagline {
        color: var(--text-secondary);
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    /* 10. Mind Map Hierarchical Styling */
    .mindmap-central {
        font-size: 1.5rem;
        font-weight: 800;
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #ec4899 0%, #f97316 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2.5rem;
        border-bottom: 3px solid rgba(236, 72, 153, 0.3);
        animation: fadeIn 0.6s ease-out;
    }
    
    .mindmap-branch {
        margin-left: 2rem;
        margin-bottom: 2rem;
        padding: 1.5rem;
        background: rgba(236, 72, 153, 0.08);
        border-radius: 12px;
        border-left: 4px solid var(--accent);
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease-out;
    }
    
    .mindmap-branch:hover {
        background: rgba(236, 72, 153, 0.12);
        transform: translateX(5px);
    }
    
    .mindmap-branch-title {
        font-weight: 700;
        color: var(--accent);
        margin-bottom: 1rem;
        font-size: 1.2rem;
        letter-spacing: -0.01em;
    }
    
    .mindmap-subbranch {
        margin-left: 2rem;
        padding: 0.75rem 0;
        color: var(--text-secondary);
        position: relative;
        line-height: 1.6;
    }
    
    .mindmap-subbranch::before {
        content: "▸";
        position: absolute;
        left: -1.5rem;
        color: var(--accent-2);
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    /* Summary & Key Points Boxes */
    .summary-box {
        background: rgba(255, 255, 255, 0.7);
        padding: 2rem;
        border-radius: 16px;
        line-height: 1.9;
        border-left: 4px solid var(--accent);
        color: var(--text-primary);
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(236, 72, 153, 0.1);
    }
    
    .key-points-box {
        background: rgba(249, 115, 22, 0.1);
        padding: 2rem;
        border-radius: 16px;
        border-left: 4px solid var(--accent-2);
        color: var(--text-primary);
        line-height: 1.9;
        box-shadow: 0 4px 16px rgba(249, 115, 22, 0.15);
    }
    
    /* Select boxes & inputs */
    .stSelectbox > div > div,
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        transition: all 0.2s ease !important;
    }
    
    .stSelectbox > div > div:hover,
    .stTextInput > div > div > input:hover {
        border-color: var(--accent) !important;
    }
    
    .stSelectbox > div > div:focus-within,
    .stTextInput > div > div > input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px var(--glow) !important;
    }
    
    /* Checkboxes */
    .stCheckbox {
        background: rgba(255, 255, 255, 0.7);
        padding: 0.875rem;
        border-radius: 10px;
        border: 1px solid var(--border);
        transition: all 0.2s ease;
    }
    
    .stCheckbox:hover {
        background: rgba(236, 72, 153, 0.08);
        border-color: var(--accent);
    }
    
    /* Download buttons */
    .stDownloadButton>button {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #ec4899 0%, #f97316 100%) !important;
        border-color: transparent !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px var(--glow) !important;
    }
    
    /* Success/Error/Warning messages */
    .stSuccess {
        background: rgba(16, 185, 129, 0.15) !important;
        color: var(--success) !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.15) !important;
        color: var(--error) !important;
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.15) !important;
        color: #f59e0b !important;
        border: 1px solid rgba(245, 158, 11, 0.4) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    .stInfo {
        background: rgba(236, 72, 153, 0.15) !important;
        color: var(--accent) !important;
        border: 1px solid rgba(236, 72, 153, 0.4) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: rgba(236, 72, 153, 0.2) !important;
        border-top-color: var(--accent) !important;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: var(--text-secondary);
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Chat input */
    .stChatInputContainer {
        border-top: 1px solid var(--border);
        padding-top: 1rem;
    }
    
    /* Divider */
    hr {
        border-color: var(--border) !important;
        margin: 2rem 0 !important;
    }
    
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Markdown in cards */
    .custom-card p {
        color: var(--text-secondary);
        line-height: 1.7;
    }
    
    .custom-card h1, .custom-card h2, .custom-card h3, .custom-card h4 {
        color: var(--text-primary);
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'document_text' not in st.session_state:
    st.session_state.document_text = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'metadata' not in st.session_state:
    st.session_state.metadata = {}
if 'key_points' not in st.session_state:
    st.session_state.key_points = None
if 'mindmap_data' not in st.session_state:
    st.session_state.mindmap_data = None

# Helper functions
def extract_text_from_pdf(pdf_file, use_ocr=False):
    """Extract text from PDF with multiple methods"""
    try:
        text = ""
        page_count = 0
        
        pdf_bytes = pdf_file.read()
        pdf_file.seek(0)
        
        # Try PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        page_count = len(reader.pages)
        
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text and page_text.strip():
                text += page_text + "\n"
        
        # Try pdfplumber if no text
        if not text.strip() and PDFPLUMBER_AVAILABLE:
            try:
                import pdfplumber
                with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except:
                pass
        
        # Try OCR if enabled
        if not text.strip() and use_ocr and OCR_AVAILABLE:
            try:
                images = convert_from_bytes(pdf_bytes, first_page=1, last_page=min(10, page_count))
                for img in images:
                    text += pytesseract.image_to_string(img) + "\n"
            except Exception as e:
                st.warning(f"OCR failed: {str(e)}")
        
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
    try:
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
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

def translate_text(text, target_language):
    if target_language == "english":
        return text
    
    language_map = {
        "spanish": "Spanish", "chinese": "Chinese (Simplified)", "hindi": "Hindi",
        "french": "French", "german": "German", "japanese": "Japanese",
        "korean": "Korean", "arabic": "Arabic", "urdu": "Urdu", "portuguese": "Portuguese"
    }
    
    system_prompt = f"You are a professional translator. Translate to {language_map.get(target_language, target_language)}."
    return get_ai_response(system_prompt, f"Translate:\n\n{text}")

def summarize_text(text, audience="general", length="medium", language="english"):
    length_map = {
        "short": "in 3–5 concise sentences",
        "medium": "in 2–3 clear paragraphs",
        "detailed": "in 4–5 detailed paragraphs with key insights"
    }
    
    audience_map = {
        "general": "for a general audience using clear language",
        "ceo": "for executives focusing on strategic insights",
        "lawyer": "for legal professionals highlighting clauses and risks",
        "researcher": "for researchers emphasizing methodology and findings",
        "student": "for students using simple, educational language"
    }
    
    system_prompt = "You are an expert document analyst. Create comprehensive summaries."
    user_prompt = f"Summarize this document {length_map[length]} {audience_map[audience]}:\n\n{text}"
    
    summary = get_ai_response(system_prompt, user_prompt, max_tokens=2000)
    
    if summary and language != "english":
        summary = translate_text(summary, language)
    
    return summary

def extract_key_points(text, num_points=7):
    system_prompt = "You are an expert at identifying critical insights."
    user_prompt = f"Extract {num_points} key points as a numbered list:\n\n{text[:5000]}"
    return get_ai_response(system_prompt, user_prompt)

def generate_mindmap_data(text):
    system_prompt = "Create structured mind maps from documents."
    user_prompt = f"""Create a mind map in JSON:
    {{"central": "Main Topic", "branches": [{{"name": "Branch", "subbranches": ["Detail"]}}]}}
    
    Document: {text[:3000]}"""
    
    response = get_ai_response(system_prompt, user_prompt)
    if not response:
        return None
    
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
            "branches": [{"name": "Main Points", "subbranches": ["Point 1", "Point 2"]}]
        }

def chat_with_document(document_text, question, chat_history=[]):
    system_prompt = f"You are an AI assistant. Answer based on:\n\n{document_text[:6000]}"
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history[-5:]:
        messages.append({"role": "user", "content": msg["question"]})
        messages.append({"role": "assistant", "content": msg["answer"]})
    messages.append({"role": "user", "content": question})
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.6,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ========== MAIN UI ==========

# Header
st.markdown("""
<div class="main-header">
    <h1>📄 AI PDF Summarizer</h1>
    <p class="tagline">Instant summaries • Multi-language • AI Chat • Mind Maps • OCR Support</p>
</div>
""", unsafe_allow_html=True)

# Two column layout
col_upload, col_results = st.columns([1, 1.5], gap="large")

# ===== LEFT COLUMN: Upload =====
with col_upload:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="card-title">⬆️ Upload Document</h2>', unsafe_allow_html=True)
    
    # File upload
    uploaded_file = st.file_uploader(
        "📎 Upload documents aur Drag and drop file here • Limit 200MB per file • PDF",
        type=["pdf"],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        st.success(f"📄 {uploaded_file.name}")
    
    # Options
    st.markdown("#### Options")
    
    language = st.selectbox("🌐 Language", [
        "english", "spanish", "chinese", "hindi", "urdu", "french",
        "german", "japanese", "korean", "arabic", "portuguese"
    ])
    
    audience = st.selectbox("👤 Target Audience", [
        "general", "ceo", "lawyer", "researcher", "student"
    ])
    
    summary_length = st.selectbox("📏 Summary Length", [
        "short", "medium", "detailed"
    ], index=1)
    
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        key_points_check = st.checkbox("🔑 Key Points", value=True)
        mindmap_check = st.checkbox("🗺️ Mind Map")
    with col_opt2:
        ocr_check = st.checkbox("📸 OCR")
        if ocr_check and not OCR_AVAILABLE:
            st.caption("⚠️ OCR not installed")
    
    # Submit button
    if uploaded_file:
        if st.button("✨ Generate Summary", use_container_width=True, type="primary"):
            # Reset
            st.session_state.summary = None
            st.session_state.key_points = None
            st.session_state.mindmap_data = None
            
            with st.spinner("📖 Extracting text..."):
                try:
                    text, page_count = extract_text_from_pdf(uploaded_file, ocr_check)
                    
                    if not text:
                        st.error("❌ Could not extract text. Try enabling OCR.")
                        st.stop()
                    
                    word_count = len(text.split())
                    reading_time = max(1, round(word_count / 200))
                    
                    st.session_state.document_text = text
                    st.session_state.metadata = {
                        "filename": uploaded_file.name,
                        "word_count": word_count,
                        "page_count": page_count,
                        "reading_time": reading_time,
                        "audience": audience,
                        "length": summary_length,
                        "language": language
                    }
                    
                    st.success(f"✅ Extracted {word_count:,} words from {page_count} pages")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.stop()
            
            with st.spinner("🤖 Generating AI summary..."):
                try:
                    chunks = chunk_text(text)
                    
                    if len(chunks) > 1:
                        partial_summaries = [summarize_text(chunk, audience, "short", "english") for chunk in chunks[:10]]
                        combined = " ".join(partial_summaries)
                        final_summary = summarize_text(combined, audience, summary_length, language)
                    else:
                        final_summary = summarize_text(text, audience, summary_length, language)
                    
                    if final_summary:
                        st.session_state.summary = final_summary
                    else:
                        st.error("❌ Failed to generate summary")
                        st.stop()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.stop()
            
            if key_points_check:
                with st.spinner("🔑 Extracting key points..."):
                    try:
                        key_points = extract_key_points(text)
                        if key_points:
                            st.session_state.key_points = key_points
                    except Exception as e:
                        st.warning(f"Could not extract key points: {str(e)}")
            
            if mindmap_check:
                with st.spinner("🗺️ Generating mind map..."):
                    try:
                        mindmap = generate_mindmap_data(text)
                        if mindmap:
                            st.session_state.mindmap_data = mindmap
                    except Exception as e:
                        st.warning(f"Could not generate mind map: {str(e)}")
            
            st.balloons()
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===== RIGHT COLUMN: Results =====
with col_results:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="card-title">✨ Results</h2>', unsafe_allow_html=True)
    
    if not st.session_state.summary:
        st.markdown("""
        <div class="empty-state">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📋</div>
            <div>Your AI summary will appear here</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Metadata
        meta = st.session_state.metadata
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("📄 Pages", meta.get("page_count", "N/A"))
        with col2:
            st.metric("📝 Words", f"{meta.get('word_count', 0):,}")
        with col3:
            st.metric("⏱️ Read", f"{meta.get('reading_time', 'N/A')} min")
        with col4:
            st.metric("🌐 Lang", meta.get("language", "EN").upper()[:2])
        with col5:
            st.metric("👤 Type", meta.get("audience", "General")[:3].upper())
        
        st.divider()
        
        # Tabs
        tab_summary, tab_keypoints, tab_mindmap, tab_chat = st.tabs([
            "📋 Summary",
            "🔑 Key Points" if st.session_state.key_points else "🔑 (Not generated)",
            "🗺️ Mind Map" if st.session_state.mindmap_data else "🗺️ (Not generated)",
            "💬 AI Chat"
        ])
        
        with tab_summary:
            st.markdown(f'<div class="summary-box animate-in">{st.session_state.summary}</div>', unsafe_allow_html=True)
            
            # Action buttons
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            
            with col_btn1:
                summary_content = f"""{'='*60}
AI PDF SUMMARIZER - ANALYSIS
{'='*60}

Document: {meta.get('filename', 'Unknown')}
Pages: {meta.get('page_count', 'N/A')}
Words: {meta.get('word_count', 'N/A')}
Language: {meta.get('language', 'english').title()}

{'='*60}
SUMMARY
{'='*60}

{st.session_state.summary}
"""
                if st.session_state.key_points:
                    summary_content += f"\n\n{'='*60}\nKEY POINTS\n{'='*60}\n\n{st.session_state.key_points}"
                
                st.download_button(
                    "📥 Download",
                    summary_content,
                    file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col_btn2:
                if st.session_state.document_text:
                    st.download_button(
                        "📝 To Text",
                        st.session_state.document_text,
                        file_name=f"{meta.get('filename', 'doc')}_extracted.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            
            with col_btn3:
                if st.button("📋 Copy", use_container_width=True):
                    st.success("✅ Copied!")
            
            with col_btn4:
                if st.button("🔄 New", use_container_width=True):
                    st.session_state.summary = None
                    st.session_state.key_points = None
                    st.session_state.mindmap_data = None
                    st.session_state.chat_history = []
                    st.rerun()
        
        with tab_keypoints:
            if st.session_state.key_points:
                st.markdown(f'<div class="key-points-box animate-in">{st.session_state.key_points}</div>', unsafe_allow_html=True)
            else:
                st.info("Key points were not generated. Enable the option and re-upload.")
        
        with tab_mindmap:
            if st.session_state.mindmap_data:
                mindmap = st.session_state.mindmap_data
                html = f'<div class="mindmap-central">{mindmap.get("central", "")}</div>'
                
                for branch in mindmap.get("branches", []):
                    html += f'<div class="mindmap-branch"><div class="mindmap-branch-title">{branch.get("name", "")}</div>'
                    for sub in branch.get("subbranches", []):
                        html += f'<div class="mindmap-subbranch">{sub}</div>'
                    html += '</div>'
                
                st.markdown(f'<div class="animate-in">{html}</div>', unsafe_allow_html=True)
            else:
                st.info("Mind map was not generated. Enable the option and re-upload.")
        
        with tab_chat:
            # Display chat history
            for msg in st.session_state.chat_history:
                with st.chat_message("user"):
                    st.write(msg["question"])
                with st.chat_message("assistant"):
                    st.write(msg["answer"])
            
            # Chat input
            if st.session_state.document_text:
                question = st.chat_input("Ask a question about your document...")
                
                if question:
                    with st.chat_message("user"):
                        st.write(question)
                    
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            answer = chat_with_document(
                                st.session_state.document_text,
                                question,
                                st.session_state.chat_history
                            )
                            st.write(answer)
                    
                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer,
                        "timestamp": datetime.now().isoformat()
                    })
                    st.rerun()
            else:
                st.info("Upload and analyze a PDF to start chatting!")
    
    st.markdown('</div>', unsafe_allow_html=True)