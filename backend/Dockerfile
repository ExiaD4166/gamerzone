# syntax=docker/dockerfile:1

FROM python:3.11-slim

# Python writes .pyc files and buffers output by default. Neither helps in a
# container: the files are thrown away with it, and buffering hides logs when the
# process is killed.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Requirements are copied and installed before the source. Docker caches each step,
# so editing application code no longer reinstalls every dependency - only the
# layers after the change are rebuilt.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Running as root inside a container means a process escape starts with root. The
# app needs no write access to its own files, so it runs as an unprivileged user.
RUN useradd --create-home --uid 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# The host platform assigns the port and passes it in as $PORT; 8000 is the local
# fallback. Binding to 0.0.0.0 rather than localhost is required for anything
# outside the container to reach it.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
