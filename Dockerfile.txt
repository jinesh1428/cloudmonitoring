FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install flask psutil google-cloud-pubsub

EXPOSE 5000

CMD ["python","dashboard/app.py"]
