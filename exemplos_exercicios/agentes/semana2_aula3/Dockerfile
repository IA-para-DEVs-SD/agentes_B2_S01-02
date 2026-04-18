FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir openai python-dotenv

COPY . .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["bash", "entrypoint.sh"]
