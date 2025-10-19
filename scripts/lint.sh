#!/usr/bin/env sh

set -e
set -x

uvx ruff check app
uvx ruff format app --check
uvx djlint --profile=jinja --check --indent 2 --preserve-blank-lines \
  --close-void-tags --max-line-length 88 app/templates/
uvx djlint --lint app/templates/
