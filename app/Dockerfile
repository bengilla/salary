FROM python:latest

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD npx tailwindcss -i ./app/static/css/input.css -o ./app/static/css/output.css --watch
CMD uvicorn main:app --host 0.0.0.0 --port 8000
