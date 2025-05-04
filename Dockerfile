FROM python:3.13-alpine
WORKDIR /app
COPY requirements.txt .
RUN apk add --no-cache --virtual .build-deps build-base \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps build-base
COPY index.py parser.py templates/ static/ /app/
EXPOSE 5000
ENV FLASK_APP=index.py
CMD ["flask", "run", "--host=0.0.0.0", "--no-reload"]