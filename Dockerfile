FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

#RUN groupadd --system echomind \
#    && useradd --system --gid echomind --create-home echomind

COPY pyproject.toml .
RUN pip install --upgrade pip \
    && pip install .

COPY pyproject.toml README.md ./

COPY app ./app
#RUN mkdir -p /app/data/documents /app/data/extractions 

#RUN chown -R echomind:echomind /app
#USER echomind

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
