FROM python:3.10-slim

WORKDIR /app

# Expose HF Spaces default port
EXPOSE 7860

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure fast server is installed
RUN pip install --no-cache-dir uvicorn fastapi

COPY . .

CMD ["uvicorn", "fast_server:app", "--host", "0.0.0.0", "--port", "7860"]
