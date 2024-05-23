FROM python:3.6.9-slim-buster AS stage1_image
LABEL stage=builder

RUN apt-get update && apt-get install -y python3-dev build-essential

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install .

FROM python:3.6.9-slim-buster AS stage2_image
COPY --from=stage1_image /opt/venv /opt/venv

ARG IMAGE_VERSION=default
LABEL version=$IMAGE_VERSION
LABEL app="cloudflare_ddns"
LABEL maintainer="PanosRCng <panosrcng@gmail.com>"

RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app

ENV PATH="/opt/venv/bin:$PATH"

ENTRYPOINT ["cloudflare_ddns"]

CMD ["-h"]