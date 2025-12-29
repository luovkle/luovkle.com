prod:
	podman-compose -f ./compose.prod.yaml up -d --build

prod-stop:
	podman-compose -f ./compose.prod.yaml down

stage:
	podman-compose -f ./compose.stage.yaml up -d --build

stage-stop:
	podman-compose -f ./compose.stage.yaml down

dev:
	podman-compose -f ./compose.dev.yaml up -d --build

dev-stop:
	podman-compose -f ./compose.dev.yaml down

local-prod:
	./.venv/bin/fastapi run --port 4000 app/main.py 

local-dev:
	./.venv/bin/fastapi dev --port 4000 app/main.py

local-dev-styles:
	pnpm run dev:css

utils-optimize-img:
	./.venv/bin/python -m cli.convert_images

utils-img-to-ansi:
	./.venv/bin/python -m cli.img_to_ansi

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

hooks:
	pre-commit run --all

hooks-install:
	pre-commit install

hooks-clean:
	pre-commit clean
