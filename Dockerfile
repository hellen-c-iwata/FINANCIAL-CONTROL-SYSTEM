# -------------------------------------------------------------------
# ESTÁGIO 1: Builder (A Fábrica Pesada)
# -------------------------------------------------------------------
FROM python:3.12 AS builder

WORKDIR /app
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# -------------------------------------------------------------------
# ESTÁGIO 2: Runner (A Imagem de Produção Leve)
# -------------------------------------------------------------------
FROM python:3.12-slim

WORKDIR /app
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY . .

RUN chown -R appuser:appgroup /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]