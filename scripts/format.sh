#!/usr/bin/env sh

set -e
set -x

.venv/bin/ruff check app --fix
.venv/bin/ruff format app
.venv/bin/djlint --profile=jinja --reformat --quiet --indent 2 \
  --preserve-blank-lines --close-void-tags --max-line-length 88 app/templates/
