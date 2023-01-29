FROM python:3.11.1-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
EXPOSE 8000
COPY . .
CMD ["uvicorn", "main:app", "--host=0.0.0.0"]