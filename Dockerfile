FROM python:3.9.5-alpine3.13

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN apk update && apk add --update --no-cache --progress \
  bash \
  tini \
  gcc \
  musl-dev \
  && rm -rf \
    /var/cache/apk/* \
    /root/.cache

WORKDIR /app

# for minimize file in docker image
COPY main.py config.py patcher.py requirements.txt ./

RUN pip install -U pip && pip install --no-cache-dir -r /app/requirements.txt

ENTRYPOINT ["tini", "--", "uvicorn", "main:app", "--host", "0.0.0.0"]
