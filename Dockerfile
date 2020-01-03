FROM python:3.6

WORKDIR /srv/app

COPY requirements-serving.txt .
COPY model/model model/model
COPY model/model.preproc model/model.preproc
COPY serving.py .
COPY entrypoint.sh .
COPY users.yaml .

RUN pip install --no-cache-dir -r requirements-serving.txt

EXPOSE 8080

ENTRYPOINT ./entrypoint.sh
