from flask import Blueprint, request, jsonify, session
from app.utils.db import get_db
from datetime import datetime

announcement_bp = Blueprint('announcement', __name__)

@announcement_bp.route('/api/announcements', methods=['GET'])
def get_announcements():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT announcement_id, title, text, created_at FROM announcements ORDER BY created_at DESC")
    result = [
        {
            "id": row[0],
            "title": row[1],
            "text": row[2],
            "created_at": row[3].strftime('%Y-%m-%d %H:%M')
        }
        for row in cur.fetchall()
    ]
    cur.close()
    return jsonify(result)

@announcement_bp.route('/api/announcements', methods=['POST'])
def add_announcement():
    data = request.get_json()
    title = data.get('title')
    text = data.get('text')
    author_id = session.get('user_id')

    if not title or not text:
        return jsonify({"success": False, "error": "Title and text are required"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO announcements (author_id, title, text, created_at)
        VALUES (%s, %s, %s, %s)
    """, (author_id, title, text, datetime.now()))
    conn.commit()
    cur.close()
    return jsonify({"success": True})

@announcement_bp.route('/api/announcements/<int:announcement_id>', methods=['PUT'])
def update_announcement(announcement_id):
    data = request.get_json()
    title = data.get('title')
    text = data.get('text')

    if not title or not text:
        return jsonify({"success": False, "error": "Title and text are required"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE announcements SET title = %s, text = %s
        WHERE announcement_id = %s
    """, (title, text, announcement_id))
    conn.commit()
    cur.close()
    return jsonify({"success": True})

@announcement_bp.route('/api/announcements/<int:announcement_id>', methods=['DELETE'])
def delete_announcement(announcement_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM announcements WHERE announcement_id = %s", (announcement_id,))
    conn.commit()
    cur.close()
    return jsonify({"success": True})
