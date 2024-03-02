FROM python:3.10.10-slim-buster

WORKDIR /app
COPY . ./
RUN apt update
RUN apt install -y tmux
RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]