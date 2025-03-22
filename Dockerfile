# Use official Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy all project files
COPY . /app

# ✅ Set environment variable for writable NLTK data directory
ENV NLTK_DATA=/app/nltk_data

# ✅ Install dependencies and pre-download NLTK data
RUN pip install --no-cache-dir -r requirements.txt && \
    python -c "import nltk; nltk.data.path.append('/app/nltk_data'); nltk.download('punkt', download_dir='/app/nltk_data')"

# Expose the necessary ports
EXPOSE 7860 8000

# Start both FastAPI and Streamlit
CMD ["sh", "-c", "uvicorn src.backend:app --host 0.0.0.0 --port 8000 & streamlit run src/app.py --server.port 7860 --server.address 0.0.0.0"]




