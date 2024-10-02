#!/usr/bin/env sh

set -e
set -x

black --check .
isort --check-only .
flake8 .
djlint --profile=jinja --check --indent 2 --preserve-blank-lines \
  --close-void-tags app/templates/
djlint --lint app/templates/
