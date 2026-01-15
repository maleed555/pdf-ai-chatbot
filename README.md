
# 🌌 3D AI Document Chatbot

A Streamlit-based AI chatbot that answers questions from uploaded PDFs, DOCX, or TXT documents using Vertex AI embeddings and LLMs. Features multi-line responses, fallback for missing context, and adjustable creativity.

---

## 🔹 Features

- Upload PDF, DOCX, TXT documents and generate embeddings.
- AI assistant with context-aware answers from your documents.
- Handles long multi-line responses.
- Debug mode to show retriever context.
- Adjustable temperature for creative or precise answers.
- Reset chat functionality.
- Clean Streamlit ChatGPT-style interface.

---

## 🔹 Tech Stack

- **Python:** 3.10  
- **Streamlit:** 1.52.2  
- **LangChain / LangChain Classic:** 1.2.3, 1.0.1  
- **LangChain-Google-VertexAI:** 3.2.1  
- **LangChain Community & Core:** 0.4.1, 1.2.7  
- **ChromaDB:** 1.4.0 (vector storage)  
- **PyPDF:** 6.6.0 (PDF parsing)  
- **docx2txt:** 0.9 (DOCX parsing)  
- **Unstructured & python-magic** (robust text extraction)  
- **Pandas:** 2.3.3 (optional data handling)  

---

## 🔹 Setup Instructions (Local)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-doc-chatbot.git
cd ai-doc-chatbot
````

### 2. Create a Virtual Environment

```bash
# Create the virtual environment
python -m venv .venv

# Activate on Linux / Mac
source .venv/bin/activate

# Activate on Windows
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Google Cloud Project ID

```bash
# Linux / Mac
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

# Windows
set GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
```

### 5. Run Streamlit Locally

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🔹 Usage

1. Upload a PDF, DOCX, or TXT file from the sidebar.
2. Ask a question in the chat input.
3. The bot retrieves context and responds.
4. Toggle **Show retriever context (debug)** to see document chunks.
5. Use **Reset Chat** to clear conversation and vectorstore.
6. Adjust temperature in `app.py` for creative answers.

---

## 🔹 Docker & GCP Cloud Run Deployment

### Dockerfile Example

```dockerfile
# 1. Python 3.10 slim image
FROM python:3.10-slim

# 2. Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# 3. Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 4. Working directory
WORKDIR /app

# 5. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy project files
COPY . .

# 7. Cloud Run default port
EXPOSE 8080

# 8. Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
```

### Build and Push Docker Image

```bash
docker build -t gcr.io/your-gcp-project-id/ai-doc-chatbot:latest .
docker push gcr.io/your-gcp-project-id/ai-doc-chatbot:latest
```

### Deploy to Cloud Run

```powershell
gcloud config set project your-gcp-project-id
gcloud run deploy ai-doc-chatbot `
  --image gcr.io/your-gcp-project-id/ai-doc-chatbot:latest `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --memory 2Gi `
  --min-instances 1 `
  --cpu 1 `
  --port 8080
```

---

## 🔹 Notes / Tips

* **Max Output Tokens:** 1024 for long answers.
* **Temperature:** 0–1 for creativity (0.6–0.7 recommended for professional answers, 0.8–0.9 for creative answers).
* **Chunk Size:** 500 chars with 100 overlap preserves context.
* **Fallback Context:** Last 2 chunks used if retriever fails.
* **Debug Mode:** Shows document chunks used by retriever.

---

## 🔹 Requirements

```
streamlit==1.52.2
langchain==1.2.3
langchain-classic==1.0.1
langchain-google-vertexai==3.2.1
langchain-community==0.4.1
langchain-core==1.2.7
pypdf==6.6.0
chromadb==1.4.0
pandas==2.3.3
docx2txt==0.9
unstructured==0.18.27
python-magic==0.4.27
pydantic==2.12.5
```

```

```


