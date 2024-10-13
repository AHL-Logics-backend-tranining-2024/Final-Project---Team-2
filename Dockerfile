FROM python:3.10-alpine

WORKDIR /app

COPY requirments.txt ./
RUN pip install -r requirments.txt

COPY app ./

ENTRYPOINT [ "fastapi", "run" , "main.py" ]