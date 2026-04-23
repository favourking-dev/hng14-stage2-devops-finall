# Stage 1: builder
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: runtime
FROM python:3.11-slim

WORKDIR /app

RUN addgroup --system app && adduser --system --group app

COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

USER app

EXPOSE 8000

HEALTHCHECK CMD curl --fail http://localhost:8000/docs || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]