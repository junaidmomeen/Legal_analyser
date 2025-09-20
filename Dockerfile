FROM python:3.13-slim

# Create a non-root user
RUN useradd --create-home appuser
USER appuser

WORKDIR /home/appuser/app

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/main.py .
COPY backend/config.py .
COPY backend/models/ ./models
COPY backend/services/ ./services
COPY backend/utils/ ./utils

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]