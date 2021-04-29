FROM python:3.9.4-slim-buster
RUN useradd -u 1234 -m exporter
USER exporter
WORKDIR /home/exporter
COPY ./requirements.txt .
RUN pip install --user --no-cache -r requirements.txt \
	&& rm requirements.txt
EXPOSE 9120
ENTRYPOINT ["python3", "export.py"]
COPY ./export.py .
