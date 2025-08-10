#!/usr/bin/env sh

set -e
set -x

sh scripts/build_highlight.sh

tailwindcss \
  -c app/assets/tailwind.config.js \
  -i app/assets/input.css \
  -o app/static/css/styles.css \
  --watch=always
