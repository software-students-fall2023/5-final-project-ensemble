FROM python:3.10-alpine
WORKDIR /web-app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 3000
CMD ["python", "server/app.py"]