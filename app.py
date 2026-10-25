from flask import Flask, render_template, request, redirect, url_for,jsonify
import sqlite3
from datetime import datetime
app = Flask(__name__)
CATEGORIES = ["Personal", "Study", "Work", "Other"]
def get_db():
    conn = sqlite3.connect("notes.db")
    conn.row_factory = sqlite3.Row
    return conn
def initialize_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(notes)").fetchall()
        }
        if "category" not in columns:
            conn.execute("""
                ALTER TABLE notes
                ADD COLUMN category TEXT NOT NULL DEFAULT 'Other'
            """)
        if "created_at" not in columns:
            conn.execute("ALTER TABLE notes ADD COLUMN created_at TEXT")
        if "updated_at" not in columns:
            conn.execute("ALTER TABLE notes ADD COLUMN updated_at TEXT")
        conn.execute("""
            UPDATE notes
            SET created_at = datetime('now', 'localtime')
            WHERE created_at IS NULL
        """)
        conn.execute("""
            UPDATE notes
            SET updated_at = created_at
            WHERE updated_at IS NULL
        """)
initialize_db()
@app.route("/")
def home():
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    query = "SELECT * FROM notes WHERE 1=1"
    params = []
    if search:
        query += " AND (title LIKE ? OR content LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term])
    if category in CATEGORIES:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY id DESC"
    with get_db() as conn:
        notes = conn.execute(query, params).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    notes = [dict(note) for note in notes]
    for note in notes:
        for field in ("created_at", "updated_at"):
            if note[field]:
                try:
                    note[field] = datetime.strptime(
                        note[field], "%Y-%m-%d %H:%M:%S"
                    ).strftime("%d %b %Y, %I:%M %p")
                except ValueError:
                    pass
    return render_template(
        "index.html",
        notes=notes,
        total=total,
        search=search,
        selected_category=category,
        categories=CATEGORIES,
    )
@app.route("/add", methods=["POST"])
def add_note():
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    category = request.form.get("category", "Other")
    if category not in CATEGORIES:
        category = "Other"
    if title and content:
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO notes
                    (title, content, category, created_at, updated_at)
                VALUES (?, ?, ?, datetime('now', 'localtime'),
                        datetime('now', 'localtime'))
            """,
                (title, content, category),
            )
    return redirect(url_for("home"))
@app.route("/edit/<int:note_id>", methods=["GET", "POST"])
def edit_note(note_id):
    with get_db() as conn:
        note = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        if note is None:
            return "Note not found", 404
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            content = request.form.get("content", "").strip()
            category = request.form.get("category", "Other")
            if category not in CATEGORIES:
                category = "Other"
            if title and content:
                conn.execute(
                    """
                    UPDATE notes
                    SET title = ?, content = ?, category = ?,
                        updated_at = datetime('now', 'localtime')
                    WHERE id = ?
                """,
                    (title, content, category, note_id),
                )
                return redirect(url_for("home"))
    return render_template("edit.html", note=note, categories=CATEGORIES)
@app.route("/delete/<int:note_id>", methods=["GET", "POST"])
def delete_note(note_id):
    with get_db() as conn:
        note = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
        if note is None:
            return "Note not found", 404
        if request.method == "POST":
            conn.execute(
                "DELETE FROM notes WHERE id = ?", (note_id,)
            )
            return redirect(url_for("home"))
    return render_template("confirm_delete.html", note=note)
# REST API: Get all notes, with optional search and category filters
@app.route("/api/notes", methods=["GET"])
def api_get_notes():
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    query = "SELECT * FROM notes WHERE 1=1"
    params = []
    if search:
        query += " AND (title LIKE ? OR content LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term])
    if category:
        if category not in CATEGORIES:
            return jsonify({"error": "Invalid category"}), 400
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY id DESC"
    with get_db() as conn:
        notes = conn.execute(query, params).fetchall()
    return jsonify([dict(note) for note in notes]), 200
# REST API: Get one note
@app.route("/api/notes/<int:note_id>", methods=["GET"])
def api_get_note(note_id):
    with get_db() as conn:
        note = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
    if note is None:
        return jsonify({"error": "Note not found"}), 404
    return jsonify(dict(note)), 200
# REST API: Create a note
@app.route("/api/notes", methods=["POST"])
def api_create_note():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400
    title = data.get("title")
    content = data.get("content")
    category = data.get("category", "Other")
    if not isinstance(title, str) or not isinstance(content, str):
        return jsonify({
            "error": "Title and content must be strings"
        }), 400
    title = title.strip()
    content = content.strip()
    if not title or not content:
        return jsonify({
            "error": "Title and content cannot be empty"
        }), 400
    if not isinstance(category, str) or category not in CATEGORIES:
        return jsonify({"error": "Invalid category"}), 400
    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO notes
                (title, content, category, created_at, updated_at)
            VALUES (?, ?, ?, datetime('now', 'localtime'),
                    datetime('now', 'localtime'))
        """, (title, content, category))
        note = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return jsonify(dict(note)), 201
# REST API: Update a note
@app.route("/api/notes/<int:note_id>", methods=["PUT"])
def api_update_note(note_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400
    title = data.get("title")
    content = data.get("content")
    category = data.get("category")
    if not isinstance(title, str) or not isinstance(content, str):
        return jsonify({
            "error": "Title and content must be strings"
        }), 400
    title = title.strip()
    content = content.strip()
    if not title or not content:
        return jsonify({
            "error": "Title and content cannot be empty"
        }), 400
    if not isinstance(category, str) or category not in CATEGORIES:
        return jsonify({"error": "Invalid category"}), 400
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
        if existing is None:
            return jsonify({"error": "Note not found"}), 404
        conn.execute("""
            UPDATE notes
            SET title = ?, content = ?, category = ?,
                updated_at = datetime('now', 'localtime')
            WHERE id = ?
        """, (title, content, category, note_id))
        note = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
    return jsonify(dict(note)), 200
# REST API: Delete a note
@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def api_delete_note(note_id):
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM notes WHERE id = ?", (note_id,)
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "Note not found"}), 404
    return jsonify({"message": "Note deleted successfully"}), 200
if __name__ == "__main__":
    app.run(debug=True)