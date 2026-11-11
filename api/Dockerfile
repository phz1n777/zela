FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY api/requirements.txt api/requirements-vision.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# COM_VISAO=1 instala o YOLO (torch em versão CPU, imagem fica ~1 GB maior).
ARG COM_VISAO=0
RUN if [ "$COM_VISAO" = "1" ]; then \
      apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
      && rm -rf /var/lib/apt/lists/* \
      && pip install --no-cache-dir -r requirements-vision.txt; \
    fi

COPY api/app ./app
# App do cidadão e painel, servidos pela própria API.
COPY web ./web
ENV WEB_DIR=/app/web

# Usuário sem privilégios (critério da disciplina de DevOps).
RUN useradd --create-home --uid 10001 zela && mkdir -p /app/uploads && chown zela /app/uploads
USER zela

EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
