FROM python:3.11-alpine

WORKDIR /code

COPY requirements.txt /code
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /code

CMD [ "python", "./bot.py" ]

