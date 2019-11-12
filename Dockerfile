FROM python:3.6-slim

COPY . /srv/Trad'UI
WORKDIR /srv/Trad'UI

RUN apt-get clean \
    && apt-get -y update
RUN apt-get -y install nginx \
    && apt-get -y install python3-dev \
    && apt-get -y install build-essential

RUN apt-get -y install libpng-dev libjpeg-dev libtiff-dev zlib1g-dev \
    && apt-get -y install gcc g++ \
    && apt-get -y install autoconf automake libtool checkinstall

RUN apt-get -y install git

RUN apt-get -y install libpcre3 libpcre3-dev
RUN pip install -r requirements.txt --src /usr/local/src

CMD ["wget http://www.leptonica.org/source/leptonica-1.73.tar.gz"]
CMD ["tar -zxvf leptonica-1.73.tar.gz"]
CMD ["./leptonica-1.73/configure"]
CMD ["make"]
CMD ["checkinstall", "-y"]
CMD ["ldconfig"]

CMD ["git clone https://github.com/tesseract-ocr/tesseract.git"]
CMD ["./tesseract/autogen.sh"]
CMD ["./tesseract/configure.sh"]
CMD ["make"]
CMD ["make install"]
CMD ["ldconfig"]

CMD ["git clone https://github.com/tesseract-ocr/tessdata.git"]
CMD ["mv", "./tessdata/*", "/usr/local/share/tessdata/"]

COPY nginx.conf /etc/nginx
RUN chmod +x ./deploy.sh
CMD ["./deploy.sh"]
