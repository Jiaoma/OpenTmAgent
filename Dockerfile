FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install prompt-toolkit requests

COPY backend/ ./backend/
COPY cli/ ./cli/

RUN mkdir -p data logs

ENV PYTHONPATH=/app:/app/backend
ENV DATABASE_URL=sqlite:///data/opentmagent.db

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
