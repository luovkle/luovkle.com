#!/usr/bin/env sh

set -e
set -x

flask run \
  --debug \
  --port 4000 \
  --host 0.0.0.0 \
  --extra-files $(echo content/**/*.md | tr ' ' ':')
