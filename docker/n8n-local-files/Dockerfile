FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --upgrade pip wheel
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY dev_os_api.py dev_os_schema.sql entrypoint.sh ./
RUN chmod +x entrypoint.sh
EXPOSE 8001
ENTRYPOINT ["./entrypoint.sh"]
