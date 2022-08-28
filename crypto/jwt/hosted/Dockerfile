FROM python:3.8-alpine

WORKDIR /jwt

COPY requirements.txt requirements.txt
RUN apk add --no-cache build-base musl-dev gmp-dev mariadb-dev
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn mysqlclient

COPY . .

CMD [ "gunicorn", "-w" , "4", "-b", "0.0.0.0", "app:app"]