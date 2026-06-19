FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --home-dir /app app

EXPOSE 8000

USER app

CMD ["python", "-c", "import time; print('TritonPath backend placeholder: FastAPI app code is not implemented yet. Container is ready.', flush=True); time.sleep(365 * 24 * 60 * 60)"]
