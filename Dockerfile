FROM python:alpine

RUN apk update 

RUN mkdir /usr/local/ldapxls
WORKDIR /usr/local/ldapxls
COPY ./requirements.txt .

RUN pip install --upgrade pip && \
   pip install -r requirements.txt && rm requirements.txt && \
   adduser -D ldapxls
COPY ./ldapxls.py .

USER ldapxls

