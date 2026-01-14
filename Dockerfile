# 1. Python 3.10 slim image use kar rahe hain (kafi light aur fast hai)
FROM python:3.10-slim

# 2. System dependencies install karna (Word aur Text files ke liye zaroori hain)
# libmagic1 file formats ko pehchanne mein madad karta hai
RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# 3. Environment variables set karna
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 4. Working directory banana
WORKDIR /app

# 5. Pehle requirements copy karke install karna (is se build fast hoti hai)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Baaki saara project copy karna
COPY . .

# 7. Cloud Run default port 8080 use karta hai
EXPOSE 8080

# 8. Streamlit ko run karne ki command
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]