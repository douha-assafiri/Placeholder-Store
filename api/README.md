# Setup
Run each command block from the repo root (`Placeholder-Store/`).

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

# API Spec
To view FastAPI's auto generated docs:
```shell
uv run uvicorn main:app --reload
```
Then navigate to: http://127.0.0.1:8000/docs
These are Fast API's generated docs on each endpoint
# Add packages
This repo uses `uv`pip.

For example: instead of `pip install fastapi` please use `uv add fastapi` for example.
This adds dependencies to the pyproject.toml

When you pull run:
`uv sync` to updated to the latest dependencies

# Run tests
```shell
uv run pytest
```

`tests/unit` needs no database. `tests/integration` uses SQLite, or MariaDB when `TEST_DB_URL` is set (e.g. `TEST_DB_URL=mysql+pymysql://store:store@127.0.0.1:3306/store uv run pytest tests/integration`).

# File structure
- `main.py`: creates the FastAPI app and adds the routes
- `routes/`: endpoints for `accounts`, `orders`, `places` and `health`
- `models.py`: database tables
- `schemas.py`: request and response models (Pydantic)
- `database.py`: database connection, set with `DB_URL`
- `config.py`: reads the environment variables
- `helpers.py`: shared helpers (database session, JWT login, password hashing)
- `initial_data.py`: sample products added on startup
- `tests/`: pytest tests (`unit/` and `integration/`), with shared fixtures in `conftest.py`
- `docker/`: Dockerfile

# Docker
If you have Docker installed, you can run the app in containers.

From the repo root, this runs the API and frontend:

```sh
JWT_SECRET=$(openssl rand -hex 32) docker compose up --build
```

On Windows, run this in Git Bash. Then open http://localhost:8080. Nginx in the frontend container forwards `/api` to the API.

MariaDB:

```sh
docker run -d --name store-db -p 3306:3306 -e MARIADB_ROOT_PASSWORD=root -e MARIADB_DATABASE=store -e MARIADB_USER=store -e MARIADB_PASSWORD=store mariadb:11
```

Then set `DB_URL=mysql+pymysql://store:store@127.0.0.1:3306/store` in `api/.env`.

See the [root README](../README.md) for full setup.
