from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import inspect

from database import engine


# FastAPI runs some code on background threads, so they must all see the same in-memory db
def test_memory_db_threads():
    with ThreadPoolExecutor() as pool:
        tables = pool.submit(lambda: inspect(engine).get_table_names()).result()
    assert "users" in tables


def test_liveness(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
