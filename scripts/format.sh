#!/usr/bin/env sh

set -e
set -x

uvx ruff check app --fix
uvx ruff format app
uvx djlint --profile=jinja --reformat --quiet --indent 2 \
  --preserve-blank-lines --close-void-tags --max-line-length 88 app/templates/
