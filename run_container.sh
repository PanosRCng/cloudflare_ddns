#!/bin/bash

docker run --rm \
 -v `pwd`/envs:/usr/src/app/envs/:ro \
 -v `pwd`/logs:/usr/src/app/logs/:rw \
 --user $(id -u ${USER}):$(id -g ${USER}) \
 --name cloudflare_ddns cloudflare_ddns:latest $*