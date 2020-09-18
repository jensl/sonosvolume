FROM node:lts AS frontend

WORKDIR /app
ADD frontend /app
RUN npm ci
RUN npm run-script build

FROM python:alpine

WORKDIR /app
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD setup.py setup.py
ADD sonosvolume sonosvolume
COPY --from=frontend /app/build sonosvolume/static-ui
RUN pip install /app

ARG speakers
ENV SPEAKERS=${speakers}

ARG discover_if
ENV DISCOVER_IF=${discover_if}

ARG port=8080
ENV PORT=$port
EXPOSE $port

CMD ["sonosvolume"]
