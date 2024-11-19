FROM python:3.12

ADD . .

RUN pip install -r requirements.txt

RUN apt-get -y update \
    && apt-get -y upgrade \
    && apt-get install -y --no-install-recommends ffmpeg

CMD ["python", "main.py"]

