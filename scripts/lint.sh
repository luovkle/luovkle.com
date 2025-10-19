#!/usr/bin/env sh

set -e
set -x

uvx ty check app
uvx ruff check app
uvx ruff format app --check
uvx djlint --check app/templates/
uvx djlint --lint app/templates/
