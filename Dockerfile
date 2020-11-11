FROM python:slim
COPY ./ /
RUN apt-get update && apt-get install --no-install-recommends nut-client -y \
	&& pip install -r /requirements.txt \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*
EXPOSE 9120
CMD /export.py
