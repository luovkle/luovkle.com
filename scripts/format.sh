#!/usr/bin/env sh

set -e
set -x

.venv/bin/autoflake --in-place .
.venv/bin/black .
.venv/bin/isort .
.venv/bin/djlint --profile=jinja --reformat --quiet --indent 2 \
  --preserve-blank-lines --close-void-tags --max-line-length 88 app/templates/
