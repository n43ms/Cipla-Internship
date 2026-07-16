FROM python:3.11-slim

WORKDIR /workspace

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend codebase to /workspace/backend
WORKDIR /workspace/backend
COPY . .

# Run uvicorn with pythonpath pointing to /workspace so backend imports work
ENV PYTHONPATH=/workspace
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
