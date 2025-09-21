FROM node:22-trixie-slim AS css-builder
RUN yarn global add pnpm
WORKDIR /css-builder/
COPY ["./package.json", "./pnpm-lock.yaml", "/css-builder/"]
RUN pnpm i --frozen-lockfile
COPY ["./app/assets/", "/css-builder/app/assets/"]
COPY ["./app/templates/", "/css-builder/app/templates"]
RUN pnpm build:css

FROM python:3.13-slim-trixie AS convert-images
ENV PIPENV_VENV_IN_PROJECT=1
RUN pip install pipenv
WORKDIR /www/
COPY ./Pipfile ./Pipfile.lock /www/
RUN pipenv install --categories=build-packages
COPY ./cli/convert_images.py /www/cli/
COPY ./app/static/images/ /www/app/static/images/
RUN /www/.venv/bin/python /www/cli/convert_images.py

FROM python:3.13-slim-trixie AS runner
ENV PIPENV_VENV_IN_PROJECT=1
RUN apt-get update && apt-get install media-types build-essential -y
RUN pip install pipenv
WORKDIR /runner
COPY ["./Pipfile", "./Pipfile.lock", "/runner/"]
RUN pipenv install
RUN apt-get remove build-essential -y && apt-get autoremove -y
COPY ["./uwsgi.ini", "/runner/"]
COPY ["./app/", "/runner/app/"]
COPY --from=css-builder \
  ["/css-builder/app/static/css/", "/runner/app/static/css/"]
RUN /runner/.venv/bin/pygmentize \
  -S github-dark -f html -a .codehilite > /runner/app/static/css/highlight.css
RUN /runner/.venv/bin/python -m whitenoise.compress /runner/app/static/
COPY --from=convert-images /www/app/static/images/ /runner/app/static/images/
COPY ["./content/", "/runner/content/"]
EXPOSE 80
CMD ["/runner/.venv/bin/uwsgi", "--ini", "uwsgi.ini"]
