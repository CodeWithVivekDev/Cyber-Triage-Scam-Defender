FROM python:3.10-slim

WORKDIR /app

# Expose HF Spaces default port
EXPOSE 7860

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for API server
RUN pip install --no-cache-dir uvicorn fastapi

# Copy all source files
COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh || true

# Use entrypoint script for intelligent routing
# If no OPENAI_API_KEY or in OpenEnv Phase 1, runs inference.py
# Otherwise starts FastAPI server for interactive use
ENTRYPOINT ["bash", "entrypoint.sh"]

