import os
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False

DATABASE = "tasks.db"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "error.log")


def log_error(message: str) -> None:
    """將錯誤訊息寫入 logs/error.log。"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{now}] {message}\n")


def get_connection() -> sqlite3.Connection:
    """建立資料庫連線。"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """初始化資料庫與 tasks 資料表。"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            done INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute("SELECT COUNT(*) AS count FROM tasks")
    count = cursor.fetchone()["count"]

    if count == 0:
        cursor.executemany(
            """
            INSERT INTO tasks (title, description, done)
            VALUES (?, ?, ?)
            """,
            [
                ("買雜貨", "牛奶、麵包、雞蛋", 0),
                ("寫作業", "完成資訊小考", 1),
            ],
        )

    conn.commit()
    conn.close()


def task_to_dict(row: sqlite3.Row) -> dict[str, object]:
    """將 sqlite3.Row 轉成 Python dict，方便 jsonify 回傳。"""
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "done": row["done"],
        "created_at": row["created_at"],
    }


@app.route("/api/tasks", methods=["GET"])
def get_tasks() -> tuple[object, int]:
    """取得所有任務。"""
    try:
        conn = get_connection()

        tasks = conn.execute(
            """
            SELECT id, title, description, done, created_at
            FROM tasks
            ORDER BY id
            """
        ).fetchall()

        conn.close()

        return jsonify({
            "message": "成功取得任務列表",
            "data": [task_to_dict(task) for task in tasks],
        }), 200

    except Exception as error:
        log_error(f"GET /api/tasks Error: {error}")

        return jsonify({
            "error": "Internal Server Error",
            "message": "伺服器內部錯誤",
        }), 500


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id: int) -> tuple[object, int]:
    """取得單一任務。"""
    try:
        conn = get_connection()

        task = conn.execute(
            """
            SELECT id, title, description, done, created_at
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

        conn.close()

        if task is None:
            return jsonify({
                "error": "Not Found",
                "message": f"找不到 ID 為 {task_id} 的任務",
            }), 404

        return jsonify({
            "message": "成功取得任務資料",
            "data": task_to_dict(task),
        }), 200

    except Exception as error:
        log_error(f"GET /api/tasks/{task_id} Error: {error}")

        return jsonify({
            "error": "Internal Server Error",
            "message": "伺服器內部錯誤",
        }), 500


@app.route("/api/tasks", methods=["POST"])
def create_task() -> tuple[object, int]:
    """建立新任務。"""
    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Bad Request",
                "message": "請求內容必須是合法 JSON",
            }), 400

        title = data.get("title")
        description = data.get("description", "")
        done = data.get("done", 0)

        if not title:
            return jsonify({
                "error": "Bad Request",
                "message": "title 為必填欄位",
            }), 400

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO tasks (title, description, done)
            VALUES (?, ?, ?)
            """,
            (title, description, int(done)),
        )

        conn.commit()
        task_id = cursor.lastrowid

        task = conn.execute(
            """
            SELECT id, title, description, done, created_at
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

        conn.close()

        return jsonify({
            "message": "任務建立成功",
            "data": task_to_dict(task),
        }), 201

    except Exception as error:
        log_error(f"POST /api/tasks Error: {error}")

        return jsonify({
            "error": "Internal Server Error",
            "message": "伺服器內部錯誤",
        }), 500


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id: int) -> tuple[object, int]:
    """更新任務。"""
    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Bad Request",
                "message": "請求內容必須是合法 JSON",
            }), 400

        title = data.get("title")
        description = data.get("description", "")
        done = data.get("done", 0)

        if not title:
            return jsonify({
                "error": "Bad Request",
                "message": "title 為必填欄位",
            }), 400

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, done = ?
            WHERE id = ?
            """,
            (title, description, int(done), task_id),
        )

        conn.commit()
        rows = cursor.rowcount

        if rows == 0:
            conn.close()

            return jsonify({
                "error": "Not Found",
                "message": f"找不到 ID 為 {task_id} 的任務",
            }), 404

        task = conn.execute(
            """
            SELECT id, title, description, done, created_at
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

        conn.close()

        return jsonify({
            "message": "任務更新成功",
            "data": task_to_dict(task),
        }), 200

    except Exception as error:
        log_error(f"PUT /api/tasks/{task_id} Error: {error}")

        return jsonify({
            "error": "Internal Server Error",
            "message": "伺服器內部錯誤",
        }), 500


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id: int) -> tuple[object, int]:
    """刪除任務。"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )

        conn.commit()
        rows = cursor.rowcount
        conn.close()

        if rows == 0:
            return jsonify({
                "error": "Not Found",
                "message": f"找不到 ID 為 {task_id} 的任務",
            }), 404

        return jsonify({
            "message": f"ID 為 {task_id} 的任務已刪除",
        }), 200

    except Exception as error:
        log_error(f"DELETE /api/tasks/{task_id} Error: {error}")

        return jsonify({
            "error": "Internal Server Error",
            "message": "伺服器內部錯誤",
        }), 500


# 啟動時初始化資料庫
init_db()