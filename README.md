<div align="center">
  <h1>⚗️ luovkle.com</h1
  <p><i>Software blog made with ❤️ by a software engineer</i></p>
</div>

---

- **URL**: <a href="https://luovkle.com" target="_blank">luovkle.com</a>
- **Source Code**: <a href="https://github.com/luovkle/luovkle.com" target="_blank">https://github.com/luovkle/luovkle.com</a>

---

## 📌 Requirements

Make sure you have the following tools installed:

- 📦 <a href="https://docs.astral.sh/uv/" target="_blank">**uv**</a> - Python dependency manager. Optional.
- 🎁 <a href="https://pnpm.io/" target="_blank">**pnpm**</a> - Node.js package manager. Optional.
- 🐳 <a href="https://podman.io/" target="_blank">**Podman**</a> - Container engine.
- 🚢 <a href="https://docs.podman.io/en/latest/markdown/podman-compose.1.html" target="_blank">**podman-compose**</a> - Compose-compatible tool for Podman.
- 🛠️ <a href="https://www.gnu.org/software/make/" target="_blank">**GNU Make**</a> - Command runner used by this project.
- 🌱 <a href="https://git-scm.com/" target="_blank">**Git**</a> - Version control system.

## 🚀 Run it locally

Running this project locally is as simple as cloning the repository and starting the Podman containers.

> **Note:** Docker compatibility is currently in progress.

### Clone the repository

```bash
git clone git@github.com:luovkle/luovkle.com.git
cd luovkle.com
```

### Run the containers

To start the containers, run the `make` command followed by the name of the environment you want to use.

Currently, the available environments are `dev`, `stage`, and `prod`.

> **Note:** Before starting any environment, make sure the required ports are available: `dev` uses ports `80` and `4000`, while `stage` and `prod` use ports `80` and `443`.

For example, to start the staging environment:

```bash
make stage
```

Once the containers are running, open `http://localhost` in your browser.

### Stop the containers

To stop the containers, run the `make` command using the following syntax:

```bash
make {ENV}-stop
```

For example, to stop the staging environment:

```bash
make stage-stop
```

## 📄 License

The content of this project is licensed under the <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank">Creative Commons Attribution 4.0 International License</a>, while the source code used to build, format, and display that content is licensed under the <a href="https://opensource.org/license/mit/" target="_blank">MIT License</a>.
