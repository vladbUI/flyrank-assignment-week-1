import sqlite3
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
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


# Malformed JSON bodies are a client error too: 400, not FastAPI's default 422
@app.exception_handler(RequestValidationError)
def bad_request(request, exc):
    return JSONResponse({"error": "Invalid request body"}, status_code=400)


def validate(body, require_title):
    title = body.get("title")
    if require_title or "title" in body:
        if not isinstance(title, str) or not title.strip():
            raise HTTPException(400, "Title is required")
    if "done" in body and not isinstance(body["done"], bool):
        raise HTTPException(400, "done must be true or false")


@app.get("/tasks")
def list_tasks():
    with db() as conn:
        return [to_task(r) for r in conn.execute("SELECT * FROM tasks")]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with db() as conn:
        return to_task(get_or_404(conn, task_id))


@app.post("/tasks", status_code=201)
def create_task(body: dict = Body(...)):
    validate(body, require_title=True)
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (body["title"].strip(), body.get("done", False)),
        )
        return to_task(get_or_404(conn, cur.lastrowid))
