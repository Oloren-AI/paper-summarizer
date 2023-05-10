FROM python:3.10-slim-bullseye
RUN pip install oloren==0.0.10a7
RUN pip install pypdf pyzotero openai
COPY app.py .
CMD python app.py