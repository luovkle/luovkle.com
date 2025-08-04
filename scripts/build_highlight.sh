#!/usr/bin/env sh

set -e
set -x

rolldown app/assets/input.js --file highlight.js --minify
mkdir -p app/static/js/ && mv highlight.js app/static/js/
mkdir -p app/static/css/ && mv highlight.css app/static/css/
