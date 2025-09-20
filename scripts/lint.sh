#!/usr/bin/env sh

set -e
set -x

.venv/bin/black --check .
.venv/bin/isort --check-only .
.venv/bin/flake8 .
.venv/bin/djlint --profile=jinja --check --indent 2 --preserve-blank-lines \
  --close-void-tags --max-line-length 88 app/templates/
.venv/bin/djlint --lint app/templates/
