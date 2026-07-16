FROM python:3.11-slim

WORKDIR /workspace

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt ./backend/
COPY ingestion/requirements.txt ./ingestion/
RUN pip install --no-cache-dir -r backend/requirements.txt -r ingestion/requirements.txt

# Copy codebase
COPY backend/ /workspace/backend/
COPY ingestion/ /workspace/ingestion/
COPY database/ /workspace/database/
COPY alembic.ini /workspace/

# Run uvicorn with pythonpath pointing to /workspace so backend and ingestion imports work
ENV PYTHONPATH=/workspace
EXPOSE 8000

WORKDIR /workspace/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
