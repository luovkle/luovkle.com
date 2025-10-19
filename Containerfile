FROM node:22-trixie-slim AS css-builder
# Install pnpm globally using yarn
RUN yarn global add pnpm
# Use `/www/` as the working directory
WORKDIR /www/
# Then, add the dependency management files and install it
COPY ./package.json ./pnpm-lock.yaml /www/
RUN pnpm i --frozen-lockfile
# Copy the asset and template files for CSS processing
COPY ./app/assets/ /www/app/assets/
COPY ./app/templates/ /www/app/templates/
# Build the CSS files with pnpm
RUN pnpm build:css


# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS convert-images-builder
# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy
# Disable Python downloads, because we want to use the system interpreter
# across both images
ENV UV_PYTHON_DOWNLOADS=0
# Install the project into `/www/`
WORKDIR /www/
# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,relabel=shared \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml,relabel=shared \
    uv sync --locked --no-install-project --only-group build
# Then, add the dependency management files and install it
# Installing separately from its dependencies allows optimal layer caching
COPY ./pyproject.toml ./uv.lock /www/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --only-group build


# Then, use an image without uv
FROM python:3.13-slim-trixie AS convert-images
# Use `/www/` as the working directory
WORKDIR /www/
# Copy the virtual environment from the convert-images-builder
COPY --from=convert-images-builder /www/.venv/ /www/.venv/
# Copy the required files for the image format conversion
COPY ./cli/convert_images.py /www/cli/
COPY ./app/static/images/ /www/app/static/images/
# Place executables in the environment at the front of the path
ENV PATH="/www/.venv/bin:$PATH"
# Run the image format conversion script
RUN python /www/cli/convert_images.py


# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS runner-builder
# Install the system dependencies
RUN apt-get update && apt-get install build-essential -y
# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy
# Disable Python downloads, because we want to use the system interpreter
# across both images
ENV UV_PYTHON_DOWNLOADS=0
# Install the project into `/www/`
WORKDIR /www/
# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,relabel=shared \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml,relabel=shared \
    uv sync --locked --no-install-project --no-dev
# Then, add the dependency management files and install it
# Installing separately from its dependencies allows optimal layer caching
COPY ./pyproject.toml ./uv.lock /www/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked  --no-dev


# Then, use a final image without uv
FROM python:3.13-slim-trixie AS runner
# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot
# Install the system dependencies
RUN apt-get update && apt-get install media-types libcap2-bin -y
# Use `/www/` as the working directory
WORKDIR /www/
# Copy the virtual environment from the runner-builder
COPY --from=runner-builder --chown=nonroot:nonroot /www/.venv/ /www/.venv/
# Place executables in the environment at the front of the path
ENV PATH="/www/.venv/bin:$PATH"
# Copy the application code
COPY ./uwsgi.ini /www/
COPY ./app/ /www/app/
# Generate the highlight.css file
RUN pygmentize \
    -S github-dark \
    -f html \
    -a .codehilite \
    > /www/app/static/css/highlight.css
# Copy the css styles from the css-builder
COPY --from=css-builder /www/app/static/css/ /www/app/static/css/
# Compress the static content
RUN python -m whitenoise.compress /www/app/static/
# Copy the images and markdown content
COPY --from=convert-images /www/app/static/images/ /www/app/static/images/
COPY ./content/ /www/content/
# Configure the nonroot user as the owner of the images directory
RUN chown -R nonroot:nonroot /www/app/static/images/
# Configure uWSGI to run on privileged ports
RUN setcap CAP_NET_BIND_SERVICE=+eip /www/.venv/bin/uwsgi
# Use the non-root user to run our application
USER nonroot
# Run the Flask application by default
EXPOSE 80
CMD ["uwsgi", "--ini", "uwsgi.ini"]
