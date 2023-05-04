FROM python:3.10-slim-bullseye
RUN pip install oloren
RUN pip install pypdf zotero openai
COPY app.py .
CMD python app.py