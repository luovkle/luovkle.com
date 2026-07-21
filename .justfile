container_engine := env(
  "CONTAINER_ENGINE",
  `which podman-compose 2>/dev/null || echo "docker compose"`
)

set default-list := true

[group("setup")]
@setup:
  uv sync --all-groups
  uv run prek install
  pnpm install --frozen-lockfile

[group("quality")]
@check:
  uv run prek run --all-files

[group("containers")]
@build environment:
  {{ container_engine }} -f ./compose.{{ environment }}.yaml build

[group("containers")]
@up environment:
  {{ container_engine }} -f ./compose.{{ environment }}.yaml up -d

[group("containers")]
@down environment:
  {{ container_engine }} -f ./compose.{{ environment }}.yaml down

[group("containers")]
[group("deployment")]
@systemd environment:
  podlet -u --override compose ./compose.{{ environment }}.yaml

[group("builders")]
@css-highlight:
  uv run pygmentize \
    -S github-dark \
    -f html \
    -a .codehilite \
    > app/static/css/highlight.css

[group("builders")]
@css-styles:
  pnpm run build:css

[group("builders")]
@img-optimize:
  uv run python -m cli.convert_images

[group("builders")]
@img-ansi:
  uv run python -m cli.img_to_ansi

[group("local")]
@fastapi port:
  uv run fastapi dev --port {{ port }} app/main.py

[group("local")]
@tailwindcss:
  pnpm run dev:css

[group("cleanup")]
[confirm("Delete generated CSS, optimized images, and cache directories?")]
@clean:
  find app/ -type d -name "ansi" -prune -print -exec rm -rf -- {} +
  find app/static/ -type d -name "author" -prune -print -exec rm -rf -- {} +
  find . -type d -name "__pycache__" -prune -print -exec rm -rf -- {} +
  find app/static/ -type f \( \
    -name "*.css" -o \
    -name "*.webp" -o \
    -name "*.avif" \
  \) -print -delete

[group("cleanup")]
[confirm("Also delete .venv, node_modules, and .ruff_cache?")]
@fclean: clean
  find . -type d \( \
    -name ".ruff_cache" -o \
    -name ".venv" -o \
    -name "node_modules" \
  \) -prune -print -exec rm -rf -- {} +
