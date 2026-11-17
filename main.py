import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

DB_PATH = Path(__file__).parent / "tasks.db"


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS tasks ("
            "id INTEGER PRIMARY KEY, title TEXT NOT NULL, done BOOLEAN NOT NULL DEFAULT 0)"
        )
        if conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [("Buy milk", False), ("Learn SQL", False), ("Walk the dog", True)],
            )


def to_task(row):
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


def get_or_404(conn, task_id):
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Task not found")
    return row


init_db()
app = FastAPI()


# Keep the Assignment 1 error shape: {"error": "..."} instead of FastAPI's {"detail": "..."}
@app.exception_handler(HTTPException)
def http_error(request, exc):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


@app.get("/tasks")
def list_tasks():
    with db() as conn:
        return [to_task(r) for r in conn.execute("SELECT * FROM tasks")]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with db() as conn:
        return to_task(get_or_404(conn, task_id))
