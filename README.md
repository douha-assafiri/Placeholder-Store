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

Run it:

```sh
uv run uvicorn main:app --reload
```

API docs: http://127.0.0.1:8000/docs

Run tests with `uv run pytest`. Add packages with `uv add <package>` (not pip).

### Frontend

```sh
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173.
