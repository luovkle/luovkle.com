#!/usr/bin/env sh

set -e
set -x

.venv/bin/ruff check app
.venv/bin/ruff format app --check
.venv/bin/djlint --profile=jinja --check --indent 2 --preserve-blank-lines \
  --close-void-tags --max-line-length 88 app/templates/
.venv/bin/djlint --lint app/templates/
