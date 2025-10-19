#!/usr/bin/env sh

set -e
set -x

uvx ruff check app --fix
uvx ruff format app
uvx djlint --reformat --quiet app/templates/
