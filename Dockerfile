# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Create non-root user
RUN adduser --disabled-password --gecos '' app

WORKDIR /app

#  СОЗДАЕМ ПАПКУ LOGS и даем права
RUN mkdir -p logs && chown -R app:app logs

#  ДАЕМ ПРАВА НА ЗАПИСЬ В РАБОЧУЮ ДИРЕКТОРИЮ
RUN chown -R app:app /app

# Copy installed packages
COPY --from=builder /root/.local /home/app/.local
COPY --chown=app:app . .

ENV PATH=/home/app/.local/bin:$PATH
ENV PYTHONPATH=/app

USER app

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
