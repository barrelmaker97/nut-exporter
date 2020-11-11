FROM python:slim
COPY ./ /
RUN apt-get update && apt-get install nut-client -y && pip install -r /requirements.txt
EXPOSE 9120
CMD /export.py
