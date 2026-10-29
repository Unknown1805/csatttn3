FROM python:3.13.18-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY app.py /app/app.py
RUN mkdir -p /lab/data && chown 1000:1000 /lab/data

USER 1000:1000
CMD ["python", "/app/app.py", "serve"]
