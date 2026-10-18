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

- `DB_URL`: the database. Without it, the API uses an in-memory SQLite database that resets when the API restarts. Use `sqlite:///dev.sqlite3` to keep data in a file, or `mysql+pymysql://store:store@127.0.0.1:3306/store` for MariaDB (see [Docker](#docker)).

The API starts with 8 sample products. To use the admin dashboard, register with the account type Staff.

Run it:

```sh
uv run uvicorn main:app --reload
```

API docs: http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/health

Run tests with `uv run pytest`. Add packages with `uv add <package>` (not pip).

`tests/unit` needs no database. `tests/integration` uses SQLite, or MariaDB when `TEST_DB_URL` is set (e.g. `TEST_DB_URL=mysql+pymysql://store:store@127.0.0.1:3306/store uv run pytest tests/integration`).

When you pull run:
`uv sync` to updated to the latest dependencies

### Frontend

```sh
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173.

Vite proxies /api → http://127.0.0.1:8000

Run tests with `npm test`. They cover the cart, checkout and API helpers, using a mocked API.

### End-to-end tests

With the API and frontend running:

```sh
cd e2e
uv sync
uv run playwright install chromium
uv run pytest
```

This runs in Chromium. CI also runs Firefox and WebKit.

The tests use the API at http://127.0.0.1:8000 and the frontend at http://localhost:5173. Set `API_URL` and `FRONTEND_URL` to test other addresses.

## Docker

If you have Docker installed, you can run the app in containers.

From the repo root:

```sh
JWT_SECRET=$(openssl rand -hex 32) docker compose up --build
```

On Windows, run this in Git Bash. Then open http://localhost:8080. Nginx in the frontend container forwards `/api` to the API.

MariaDB:

```sh
docker run -d --name store-db -p 3306:3306 -e MARIADB_ROOT_PASSWORD=root -e MARIADB_DATABASE=store -e MARIADB_USER=store -e MARIADB_PASSWORD=store mariadb:11
```

Then set `DB_URL=mysql+pymysql://store:store@127.0.0.1:3306/store` in `api/.env`.

## CI/CD

- **CI** (`.github/workflows/ci.yml`) runs on every pull request: API lint, unit and integration tests (on SQLite and MariaDB), frontend lint, tests and build, Playwright tests (customer and staff journeys), and Docker image builds. All checks must pass before merging.
- **CD** (`.github/workflows/cd.yml`) runs after CI passes on `main` and pushes both images to Docker Hub.

## Contributing

`main` is protected. Create a branch, push it, and open a pull request. It can be merged once all CI checks pass.
