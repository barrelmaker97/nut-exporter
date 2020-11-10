FROM python:slim
COPY ./ /
RUN apt update && apt install nut-client -y && pip install -r /requirements.txt
EXPOSE 9120
CMD /export.py
