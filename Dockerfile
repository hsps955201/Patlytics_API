FROM python:3.11-slim

WORKDIR /Patlytics_API

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
        gettext-base \ 
    && rm -rf /var/lib/apt/lists/*


RUN mkdir -p /root/.aws
COPY aws/ ./aws/
RUN envsubst < ./aws/credentials.template > /root/.aws/credentials \
    && cp ./aws/config.template /root/.aws/config \
    && chmod 600 /root/.aws/credentials /root/.aws/config

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "app.py"]