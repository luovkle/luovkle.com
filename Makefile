prod:
	podman-compose -f ./docker-compose.prod.yaml up -d --build

prod-stop:
	podman-compose -f ./docker-compose.prod.yaml down

dev:
	podman-compose -f ./docker-compose.dev.yaml up -d --build

dev-stop:
	podman-compose -f ./docker-compose.dev.yaml down

convert-images:
	./.venv/bin/python ./cli/convert_images.py
