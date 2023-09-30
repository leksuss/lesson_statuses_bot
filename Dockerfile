FROM python:3.9-slim

WORKDIR /opt/app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./src /opt/app
CMD python bot.py --chat_id=${CHAT_ID}
