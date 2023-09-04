FROM ubuntu:20.04

RUN apt-get update && apt-get install --no-install-recommends -y \
    python3-dev \
    python3-pip \
&& rm -rf /var/lib/apt/lists/*

RUN mkdir /app
COPY app /app
COPY requirements.txt /app
WORKDIR /app

RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

RUN chown -R root:root /app

USER root

EXPOSE 80

ENTRYPOINT [ "gunicorn" ]
CMD ["--bind", "0.0.0.0:80", "entrypoint:app"]