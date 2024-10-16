# linkpulse

This is an empty project right now. It merely holds a simplistic FastAPI server to showcase Railway.

- Windows WSL is recommended for development. See [here][wsl] for setup instructions.

## Project Structure

- `/backend` A backend server using [FastAPI][fastapi], managed with [Poetry][poetry].
- `/frontend` A frontend server using [React][react], managed with [pnpm][pnpm].

## Setup

### Frontend

1. Install Node.js 22.x
<!-- TODO: Add details on installation practices, asdf + nvm -->
3. Install `pnpm` with `npm install -g pnpm`
4. Install frontend dependencies with `pnpm install`
5. Start the frontend server with `./run.sh`

<!-- TODO: Get local Caddy server with Vite builds working. -->

### Backend

1. Install [`pyenv`][pyenv] or [`pyenv-win`][pyenv-win]
    
    - Install Python 3.12 (`pyenv install 3.12`)

2. Install `poetry`

    - Requires `pipx`, see [here][pipx]
    - Install with `pipx install poetry`

3. Install backend dependencies with `poetry install`.
4. Start the backend server with `./run.sh`


## Usage

- A fully editable (frontend and backend), automatically reloading project is possible, but it requires two terminals.
  - Each terminal must start in the respective directory (`/backend` and `/frontend`).
  - `./run.sh` will start the development server in the respective directory.
    - The first argument is optional, but can be used in the frontend to compile & serve the backend.


[fastapi]: https://fastapi.tiangolo.com/
[poetry]: https://python-poetry.org/
[react]: https://react.dev/
[pnpm]: https://pnpm.io/
[wsl]: https://docs.microsoft.com/en-us/windows/wsl/install
[pipx]: https://pipx.pypa.io/stable/installation/
[pyenv]: https://github.com/pyenv/pyenv
[pyenv-win]: https://github.com/pyenv-win/pyenv-win