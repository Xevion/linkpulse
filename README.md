# linkpulse

A project for monitoring websites, built with FastAPI and React.

## Structure

A description of the project's folder structure.

- `/backend` A backend server using [FastAPI][fastapi], managed with [Poetry][poetry].
  - `/backend/linkpulse` A python module containing the FastAPI application, database models, migration scripts, and more.
  - `/backend/migrations` Migration scripts for [`peewee`][peewee]; most of this is generated automatically.
- `/frontend` A frontend server using [React][react], managed with [pnpm][pnpm], built with [Vite][vite].
  - `/frontend/Caddyfile` A Caddy configuration file used for proxying API requests to the backend server via Private Networking (Railway).
  - `/frontend/nixpacks.toml` Configures the frontend build process for Nixpacks, enabling the use of Caddy for deployment.

## Setup

Windows WSL is **strongly recommended** for development. See [here][wsl] for setup instructions.

The following instructions were written for Ubuntu 22.04 LTS, the primary (default) target for WSL.

### Frontend

1. Install Node.js 22.x

I recommend [`asdf`][asdf] or [`nvm`][nvm] for managing this (although `asdf` is superior in my opinion, and it's tool/language agnostic). [Alternatives are available though](https://nodejs.org/en/download/package-manager).

Assuming you're using Bash/Zsh & Git, you'll need to add this to your bashrc file: `. "$HOME/.asdf/asdf.sh"`. Shell completions are recommended, but optional. Refer to documentation [here][asdf-install] for further detail.

Once added, restart your terminal and `cd` into the project root.

```
asdf plugin add nodejs
asdf install
```

This installs the version of Node.js specified in [`.tool-versions`](.tool-versions).

>[!NOTE] If you use Node.js for other projects, you may want to install the version you need & set it as the global version via `asdf global nodejs <version>` or `asdf install nodejs latest:<version>`. If you don't care, `asdf install latest nodejs` also works.

2. Install `pnpm` with `npm install -g pnpm`
3. `cd frontend`
4. Install frontend dependencies with `pnpm install`
5. Start the frontend server with `./run.sh`

<!-- TODO: Get local Caddy server working. -->

### Backend

1. Install [`pyenv`][pyenv] or [`pyenv-win`][pyenv-win]
    
    - Install Python 3.12 (`pyenv install 3.12`)

2. Install `poetry`

    - Requires `pipx`, see [here][pipx]. You will NOT have this by default. This is NOT `pip`, do not install either with `pip`.
    - Install with `pipx install poetry`

3. Install backend dependencies with `poetry install`.
4. Start the backend server with `./run.sh`
5. (*optional*) Install the [Railway CLI][railway]
   - Fastest installation is via shell: `bash <(curl -fsSL cli.new)`
     - Alternatives found [here][railway].
   - This will let us skip creating a local `.env` file, as well as keeping your database URL synchronized.
   - You will have to run `railway login` upon install as well as `railway link` in the backend directory.

## Usage

A full stack (*frontend* and *backend*), automatically reloading project is possible, but it requires two terminals.
  
1. Open a terminal in each respective directory (`/backend` and `/frontend`).
2. Execute `./run.sh` to start the development server for each.
    - For the backend, you'll either need to have the `railway` CLI installed or a `.env` file with the database URL.
      - See [`.env.example`](backend/.env.example) for a list of all available environment variables.
    - For the frontend, the defaults are already sufficient.

>[!WARNING] The `run.sh` scripts provide default environment variables internally; if you want to run the commands manually, you'll need to provide them to `.env` files or the command line.

[peewee]: https://docs.peewee-orm.com/en/latest/
[railway]: https://docs.railway.app/guides/cli
[vite]: https://vite.dev/
[asdf]: https://asdf-vm.com/
[asdf-install]: https://asdf-vm.com/guide/getting-started.html#_3-install-asdf
[nvm]: https://github.com/nvm-sh/nvm
[fastapi]: https://fastapi.tiangolo.com/
[poetry]: https://python-poetry.org/
[react]: https://react.dev/
[pnpm]: https://pnpm.io/
[wsl]: https://docs.microsoft.com/en-us/windows/wsl/install
[pipx]: https://pipx.pypa.io/stable/installation/
[pyenv]: https://github.com/pyenv/pyenv
[pyenv-win]: https://github.com/pyenv-win/pyenv-win