FROM python:3.6-slim

# --- System deps (cached until Dockerfile changes) ---
RUN sed -i '/security/d' /etc/apt/sources.list \
    && sed -i 's|http://deb.debian.org|http://archive.debian.org|g' /etc/apt/sources.list \
    && rm -f /etc/apt/sources.list.d/* \
    && apt-get clean \
    && apt-get -y update

RUN apt-get -y install wget nginx python3-dev build-essential \
    libpng-dev libjpeg-dev libtiff-dev zlib1g-dev \
    libsm6 libxext6 libxrender1 libglib2.0-0 \
    gcc g++ cmake pkg-config \
    autoconf automake libtool \
    tesseract-ocr libtesseract-dev tesseract-ocr-eng tesseract-ocr-fra \
    git libpcre3 libpcre3-dev

# --- Python deps (cached until requirements.txt changes) ---
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && pip install uwsgi

# --- App code (rebuilds fast, only this layer invalidated) ---
COPY . /srv/ui-detector
WORKDIR /srv/ui-detector
RUN mkdir -p /srv/ui-detector/uploads /srv/ui-detector/results_prediction /srv/ui-detector/output \
    && chown -R www-data:www-data /srv/ui-detector \
    && chmod -R 775 /srv/ui-detector/uploads /srv/ui-detector/results_prediction /srv/ui-detector/output

COPY nginx.conf /etc/nginx
RUN sed -i 's/\r$//' deploy.sh && chmod +x deploy.sh

CMD ["./deploy.sh"]
