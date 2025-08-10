FROM node:22-alpine3.20 AS css-builder
RUN yarn global add pnpm
WORKDIR /css-builder/
COPY ["./package.json", "./pnpm-lock.yaml", "/css-builder/"]
RUN pnpm i --frozen-lockfile
COPY ["./scripts/build_highlight.sh", "/css-builder/scripts/build_highlight.sh"]
COPY ["./app/assets/", "/css-builder/app/assets/"]
COPY ["./app/templates/", "/css-builder/app/templates"]
RUN pnpm build:css
RUN pnpm build:highlight

FROM python:3.12-slim-bookworm AS runner
RUN apt-get update && apt-get install media-types build-essential -y
RUN pip install pipenv
WORKDIR /runner
COPY ["./Pipfile", "./Pipfile.lock", "/runner/"]
RUN pipenv install
RUN apt-get remove build-essential -y && apt-get autoremove -y
COPY ["./app/", "/runner/app/"]
COPY --from=css-builder \
  ["/css-builder/app/static/css/", "/runner/app/static/css/"]
COPY --from=css-builder \
  ["/css-builder/app/static/js/", "/runner/app/static/js/"]
COPY ["./content/", "/runner/content/"]
EXPOSE 80
CMD ["pipenv", "run", "prod"]
