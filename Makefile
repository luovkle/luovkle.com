prod:
	podman-compose -f ./docker-compose.prod.yaml up -d --build

prod-stop:
	podman-compose -f ./docker-compose.prod.yaml down

dev:
	podman-compose -f ./docker-compose.dev.yaml up -d --build

dev-stop:
	podman-compose -f ./docker-compose.dev.yaml down

local-prod:
	./.venv/bin/uwsgi --ini ./uwsgi.ini

local-dev:
	./.venv/bin/flask run --debug --port 4000

local-dev-styles:
	pnpm run dev:css

utils-optimize-img:
	./.venv/bin/python ./cli/convert_images.py

utils-highlight-css:
	./.venv/bin/pygmentize \
		-S github-dark \
		-f html \
		-a .codehilite \
		> ./app/static/css/highlight.css

utils-styles-css:
	pnpm run build:css

format:
	sh ./scripts/format.sh

lint:
	sh ./scripts/lint.sh
