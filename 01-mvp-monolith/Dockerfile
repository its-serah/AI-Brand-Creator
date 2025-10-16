FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN mkdir -p storage
ENV PORT=8080
EXPOSE 8080
CMD python server.py
