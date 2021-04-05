FROM python:3.9.3-slim-buster
COPY ./requirements.txt /
RUN apt-get update && apt-get install --no-install-recommends nut-client -y \
	&& pip install -r /requirements.txt \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*
EXPOSE 9120
ENTRYPOINT ["python3", "/export.py"]
COPY ./export.py /
