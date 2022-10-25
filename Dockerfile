FROM python:3.11.0-alpine
RUN adduser --disabled-password --gecos "" --uid "1234" "exporter"
USER exporter
WORKDIR /home/exporter
COPY ./requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt \
	&& rm requirements.txt
EXPOSE 9120
ENTRYPOINT ["python3", "export.py"]
COPY ./export.py .
