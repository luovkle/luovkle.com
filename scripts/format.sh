#!/usr/bin/env sh

set -e
set -x

autoflake --in-place .
black .
isort .
djlint --profile=jinja --reformat --quiet --indent 2 --preserve-blank-lines \
  --close-void-tags --max-line-length 88 app/templates/
