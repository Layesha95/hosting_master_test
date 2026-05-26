from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_FILE = os.path.join("..", "database", "business.db")

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            service TEXT,
            date TEXT,
            time TEXT,
            message TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def dict_from_row(row):
    return {
        "id": row[0],
        "name": row[1],
        "phone": row[2],
        "service": row[3],
        "date": row[4],
        "time": row[5],
        "message": row[6],
        "status": row[7],
        "created_at": row[8]
    }


@app.route("/")
def home():
    return jsonify({"status": "SQLite backend running"})


@app.route("/login", methods=["POST"])
def login():
    data = request.json

    if data.get("username") == ADMIN_USERNAME and data.get("password") == ADMIN_PASSWORD:
        return jsonify({"success": True, "message": "Login successful"})

    return jsonify({"success": False, "message": "Invalid username or password"})


@app.route("/booking", methods=["POST"])
def create_booking():
    data = request.json

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO bookings
        (name, phone, service, date, time, message, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name", ""),
        data.get("phone", ""),
        data.get("service", ""),
        data.get("date", ""),
        data.get("time", ""),
        data.get("message", ""),
        "Pending",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    booking_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "success": True,
        "message": "Booking saved successfully",
        "id": booking_id
    })


@app.route("/bookings", methods=["GET"])
def get_bookings():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, phone, service, date, time, message, status, created_at
        FROM bookings
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    bookings = [dict_from_row(row) for row in rows]

    return jsonify(bookings)


@app.route("/booking/<int:booking_id>", methods=["DELETE"])
def delete_booking(booking_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    deleted_count = cursor.rowcount

    conn.commit()
    conn.close()

    if deleted_count == 0:
        return jsonify({"success": False, "message": "Booking not found"}), 404

    return jsonify({"success": True, "message": "Booking deleted successfully"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
