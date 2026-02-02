
# 🚀 AI PDF Summarizer - Advanced Document Intelligence

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

**Transform any PDF into actionable insights with AI-powered analysis**

---

## ✨ Key Features

### 📄 **Instant Summaries**
- Upload PDFs up to **50MB** and get summaries in seconds
- Works with **scanned documents** using OCR technology
- No account required, no installation needed
- Process documents of any length

### 🌐 **Multi-Language Support**
Summarize PDFs in 11+ languages:
- English, Spanish, Chinese, Hindi, Urdu
- French, German, Japanese, Korean
- Arabic, Portuguese

### 💬 **AI Chat & Follow-Up**
- Ask questions about your document
- Clarify specific points
- Explore sections in depth
- Get instant AI-powered answers

### 📝 **Text Extraction & Conversion**
- Convert PDFs to plain text
- Easy copying and downloading
- Perfect for further analysis
- Works with scanned PDFs (OCR)

### 🧠 **Mind Map Generation**
- Visualize document structure
- Better comprehension and study
- Hierarchical organization
- Interactive exploration

### 🎯 **Smart Analysis**
- Extract key points automatically
- Target different audiences (CEO, Lawyer, Student, etc.)
- Customizable summary lengths
- Professional formatting

### 💻 **Cross-Platform**
- Works on Windows, Mac, Linux
- Mobile-friendly interface
- Access from anywhere
- No installation required

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Tesseract OCR (for scanned PDFs)
- Groq API key (free from [console.groq.com](https://console.groq.com))

### Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install Tesseract OCR:**

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install poppler-utils
```

**macOS:**
```bash
brew install tesseract
brew install poppler
```

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Download Poppler: https://github.com/oschwartz10612/poppler-windows/releases

3. **Setup environment:**
```bash
cp env.example .env
# Edit .env and add your GROQ_API_KEY
```

4. **Run the application:**
```bash
python app.py
```

5. **Open browser:**
```
http://localhost:5000
```

---

## 📖 Usage Guide

### Basic Workflow

1. **Upload PDF**
   - Click upload area or drag & drop
   - Supports files up to 50MB
   - Works with regular and scanned PDFs

2. **Configure Options**
   - Select language for summary
   - Choose target audience
   - Pick summary length
   - Enable key points extraction
   - Enable mind map generation
   - Enable OCR for scanned PDFs

3. **Generate Summary**
   - Click "Generate Summary"
   - Wait for AI processing (10-30 seconds)
   - View results in tabs

4. **Explore Results**
   - **Summary Tab**: Main AI-generated summary
   - **Key Points Tab**: Important bullet points
   - **Mind Map Tab**: Visual structure
   - **AI Chat Tab**: Ask questions

5. **Export**
   - Copy to clipboard
   - Download formatted summary
   - Convert to plain text
   - Start new document

---

## 🎨 Features in Detail

### 1. Instant Summaries
```
✓ Process documents in seconds
✓ Handle large files (50MB+)
✓ Support scanned PDFs with OCR
✓ No registration required
```

### 2. Multi-Language Support
```
✓ Summarize in 11+ languages
✓ Auto-translation capability
✓ Maintains context and meaning
✓ Professional quality output
```

### 3. AI Chat Interface
```
✓ Ask follow-up questions
✓ Clarify confusing points
✓ Deep dive into sections
✓ Context-aware responses
```

### 4. Text Extraction
```
✓ Convert PDF to text
✓ Extract from scanned docs
✓ Download as .txt file
✓ Easy copying
```

### 5. Mind Map Visualization
```
✓ Hierarchical structure
✓ Visual organization
✓ Better comprehension
✓ Study-friendly format
```

### 6. Customization Options
```
✓ 5 Audience types
✓ 3 Summary lengths
✓ Key points extraction
✓ Multiple languages
```

---

## 🔧 API Endpoints

### Upload & Summarize
```http
POST /upload
Content-Type: multipart/form-data

Parameters:
- file: PDF file
- language: Language code
- audience: Target audience
- summary_length: short/medium/detailed
- include_key_points: true/false
- include_mindmap: true/false
- use_ocr: true/false
```

### AI Chat
```http
POST /chat
Content-Type: application/json

Body:
{
  "session_id": "xxx",
  "question": "Your question"
}
```

### Convert to Text
```http
POST /convert-to-text
Content-Type: application/json

Body:
{
  "session_id": "xxx"
}
```

### Download Summary
```http
POST /download
Content-Type: application/json

Body: {
  "summary": "...",
  "key_points": "...",
  "metadata": {...}
}
```

---

## 📁 Project Structure

```
ai-pdf-summarizer/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                   # API keys (create from env.example)
├── env.example            # Environment template
├── README.md              # This file
│
├── templates/
│   └── index.html         # Web interface
│
└── uploads/               # Temporary storage (auto-created)
```

---

## ⚙️ Configuration

### Environment Variables
```bash
GROQ_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here  # Optional
```

### Customization

**Adjust file size limit:**
```python
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB
```

**Change AI model:**
```python
model="llama-3.3-70b-versatile"  # Current model
```

**Modify summary prompts:**
Edit the `summarize_text()` function in `app.py`

---

## 🛠️ Troubleshooting

### OCR Not Working
```bash
# Check Tesseract installation
tesseract --version

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

### PDF2Image Issues
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler
```

### Large Files Timing Out
- Increase timeout in your server config
- Use streaming for very large files
- Consider splitting documents

### Memory Issues
- Process fewer chunks at once
- Reduce max_tokens in AI calls
- Use pagination for large docs

---

## 🚀 Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app --timeout 120
```

### Docker
```dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📊 Performance Tips

1. **Optimize Processing**
   - Use chunking for large documents
   - Cache frequently accessed summaries
   - Implement background jobs for long tasks

2. **Scale Horizontally**
   - Use load balancer
   - Deploy multiple instances
   - Implement Redis for session storage

3. **Database Integration**
   - Store summaries in database
   - Cache AI responses
   - Track usage analytics

---

## 🔒 Security Best Practices

- Never commit `.env` file
- Use environment variables for secrets
- Implement rate limiting
- Validate file uploads
- Sanitize user inputs
- Use HTTPS in production

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch
3. Make your changes
4. Add tests
5. Submit pull request

---

## 📝 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- **Groq**: Fast AI inference
- **Flask**: Web framework
- **PyPDF2**: PDF processing
- **Tesseract**: OCR engine
- **pdf2image**: PDF to image conversion

---

## 📧 Support

For issues or questions:
- Open GitHub issue
- Email: engrrabdulkhaliq.com


---

<div align="center">

**Built with ❤️ and AI**

⭐ Star this repo if helpful!

</div>
