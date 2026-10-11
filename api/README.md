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