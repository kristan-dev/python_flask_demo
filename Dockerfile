FROM python:3.6

ARG PROJECT_HOME=/usr/local/flask_demo

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

WORKDIR ${PROJECT_HOME}
COPY ./conf /conf
COPY ./database /database
COPY ./src /src
COPY ./config.py /config.py
COPY ./app.py /app.py
CMD [ "python", "/app.py"]