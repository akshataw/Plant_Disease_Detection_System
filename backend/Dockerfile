FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TF_CPP_MIN_LOG_LEVEL=2 \
    FLASK_APP=wsgi.py

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Non-root user; UID 1000 matches the typical host user so bind-mounted models/ stays writable
RUN useradd --uid 1000 --create-home appuser \
    && mkdir -p /app/uploads /app/models && chown -R appuser:appuser /app
COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 5000
ENTRYPOINT ["./entrypoint.sh"]
