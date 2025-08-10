#!/usr/bin/env sh

set -e
set -x

flask run \
  --debug \
  --port 4000 \
  --extra-files $(echo content/**/*.md | tr ' ' ':')
