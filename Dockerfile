FROM python:3.9.4-slim-buster
COPY ./requirements.txt /
RUN pip install -r /requirements.txt
EXPOSE 9120
ENTRYPOINT ["python3", "/export.py"]
COPY ./export.py /
