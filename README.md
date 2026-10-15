# Placeholder-Store

SWE40006 group project: a web store with a **FastAPI** backend (`api/`) and a **React + Vite** frontend (`frontend/`).

## Install tools

You need **Git**, **uv** (manages Python for the API) and **Node.js** (for the frontend).

**macOS** (with [Homebrew](https://brew.sh/)):

```sh
brew install git uv node
```

**Windows** (PowerShell):

```powershell
winget install Git.Git astral-sh.uv OpenJS.NodeJS.LTS
```

Restart your terminal afterwards, then check everything worked:

```sh
git --version
uv --version
node --version   # should be 22 or newer
```

Other options: [uv install guide](https://docs.astral.sh/uv/getting-started/installation/), [Node.js downloads](https://nodejs.org/).

## Get the code

```sh
git clone https://github.com/douha-assafiri/Placeholder-Store.git
cd Placeholder-Store
```

## Setup

Run each command block from the repo root (`Placeholder-Store/`).

### API

```sh
cd api
uv sync
```

Create `api/.env` with a random secret (run inside `api/`):

macOS / Linux:

```sh
cat > .env <<EOF
JWT_SECRET=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRATION=1
EOF
```

Windows (PowerShell):

```powershell
@"
JWT_SECRET=$([guid]::NewGuid().ToString('N'))$([guid]::NewGuid().ToString('N'))
JWT_ALGORITHM=HS256
JWT_EXPIRATION=1
"@ | Set-Content -Encoding ascii .env
```

Optional settings for `api/.env`:

- `ADMIN_EMAIL` and `ADMIN_PASSWORD`: creates a staff account when the API starts, for the admin dashboard.
- `DB_URL`: the database. Without it, the API uses an in-memory SQLite database that resets when the API restarts. Use `sqlite:///dev.sqlite3` to keep data in a file, or `mysql+pymysql://store:store@127.0.0.1:3306/store` for MariaDB (see [Docker](#docker)).

The API starts with 8 sample products.

Run it:

```sh
uv run uvicorn main:app --reload
```

API docs: http://127.0.0.1:8000/docs

Run tests with `uv run pytest`. Add packages with `uv add <package>` (not pip).

When you pull run:
`uv sync` to updated to the latest dependencies

### Frontend

```sh
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173.

The frontend uses the API at http://127.0.0.1:8000. To use another address, set `VITE_API_URL`, for example `VITE_API_URL=http://127.0.0.1:9000 npm run dev`.

### End-to-end tests

With the API and frontend running:

```sh
cd e2e
uv sync
uv run playwright install chromium
uv run pytest
```

This runs in Chromium. CI also runs Firefox and WebKit.

The admin test needs the staff account from `api/.env`. Pass the same values, for example `ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD=secret123 uv run pytest`, otherwise it is skipped.

The tests use the API at http://127.0.0.1:8000 and the frontend at http://localhost:5173. Set `API_URL` and `FRONTEND_URL` to test other addresses.

## Docker

If you have Docker installed, you can run the app in containers.

API:

```sh
cd api
touch dev.sqlite3
cd docker
JWT_SECRET=$(openssl rand -hex 32) docker compose up --build
```

On Windows, run this in Git Bash. To also create a staff account, add `ADMIN_EMAIL` and `ADMIN_PASSWORD` before `docker compose`.

Frontend:

```sh
docker build -f frontend/docker/Dockerfile -t placeholder-store-frontend frontend
docker run -p 8080:80 placeholder-store-frontend
```

Then open http://localhost:8080. To point the image at another API, add `--build-arg VITE_API_URL=<api address>` to `docker build`.

MariaDB:

```sh
docker run -d --name store-db -p 3306:3306 -e MARIADB_ROOT_PASSWORD=root -e MARIADB_DATABASE=store -e MARIADB_USER=store -e MARIADB_PASSWORD=store mariadb:11
```

Then set `DB_URL=mysql+pymysql://store:store@127.0.0.1:3306/store` in `api/.env`.

## CI/CD

- **CI** (`.github/workflows/ci.yml`) runs on every pull request: API lint and tests, frontend lint and build, Playwright tests (customer and staff journeys), and Docker image builds. All checks must pass before merging.
- **CD** (`.github/workflows/cd.yml`) runs after CI passes on `main` and pushes both images to Docker Hub.

## Contributing

`main` is protected. Create a branch, push it, and open a pull request. It can be merged once all CI checks pass.
