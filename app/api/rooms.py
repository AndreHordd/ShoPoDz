from flask import Blueprint, jsonify
from app.utils.db import get_db

room_bp = Blueprint('room', __name__)

@room_bp.route('/api/rooms')
def get_rooms():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT room_id, room_number FROM rooms")
    data = [{"id": row[0], "number": row[1]} for row in cur.fetchall()]
    cur.close()
    return jsonify(data)
