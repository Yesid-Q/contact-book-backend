FROM python:3.10.6-alpine3.15

WORKDIR /src/app

COPY . .

RUN pip3 install -r requirements.txt

ENV PORT=8080

EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --reload --host 0.0.0.0 --port $PORT"]