# Use python 3.9
FROM python:3.9-slim

WORKDIR /app

# Copy requirement first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything
COPY . .

# Exposure
EXPOSE 8501
EXPOSE 7860

# Start both FastAPI and Streamlit
# FastAPI on 7860 (Main port for Phase 1 check)
# Streamlit on 8501 (Accessible via proxy)
CMD uvicorn server.app:app --host 0.0.0.0 --port 7860 & streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0