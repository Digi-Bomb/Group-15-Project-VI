#docker python versions can use slim or alpine for smaller images
#this file was mostly copied from softsec assignment
FROM python:3.11

WORKDIR /app

COPY ../requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app/ .

EXPOSE 5000

CMD ["python", "app.py"]
