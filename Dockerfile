# 1. Base Image: official lightweight Python runtime
FROM python:3.12-slim

# 2. Working Directory: internal container directory
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# 3. Dependencies: copy the manifest first so this layer is cached between code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Application Code & Startup Command (Gunicorn WSGI server, non-root user).
#    One worker + threads: the default SQLite DB is in-memory per process, so all requests must share one process.
COPY . .
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "app:create_app()"]
