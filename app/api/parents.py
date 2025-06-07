from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from app.utils.db import get_db

parent_bp = Blueprint('parent', __name__)

@parent_bp.route('/parent')
def parent_dashboard():
    if session.get('role') != 'parent':
        return redirect(url_for('auth.login'))
    return render_template('parent/parent_dashboard.html')

@parent_bp.route('/api/parents', methods=['GET'])
def get_parents():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, first_name, last_name, phone FROM parents")
    rows = cur.fetchall()
    cur.close()
    return jsonify([dict(zip(['user_id', 'first_name', 'last_name', 'phone'], row)) for row in rows])

@parent_bp.route('/api/parents', methods=['POST'])
def add_parent():
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone = data.get('phone')

    if not first_name or not last_name or not phone:
        return jsonify({'error': 'Missing data'}), 400

    conn = get_db()
    cur = conn.cursor()

    # 🔸 Додаємо запис у таблицю users
    cur.execute("""
        INSERT INTO users (email, password_hash, role)
        VALUES (%s, %s, %s)
        RETURNING user_id
    """, (f"{last_name.lower()}_{first_name.lower()}@school.local", 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'parent'))
    user_id = cur.fetchone()[0]

    # 🔸 Додаємо в таблицю parents
    cur.execute("""
        INSERT INTO parents (user_id, first_name, last_name, phone)
        VALUES (%s, %s, %s, %s)
    """, (user_id, first_name, last_name, phone))

    conn.commit()
    cur.close()
    return jsonify({'success': True})

@parent_bp.route('/api/parents/<int:user_id>', methods=['PUT'])
def update_parent(user_id):
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone = data.get('phone')

    email = f"{last_name.lower()}.{first_name.lower()}@school.local"

    conn = get_db()
    cur = conn.cursor()

    # Оновити таблицю users
    cur.execute("UPDATE users SET email = %s WHERE user_id = %s", (email, user_id))

    # Оновити таблицю parents
    cur.execute("""
        UPDATE parents
        SET first_name = %s, last_name = %s, phone = %s
        WHERE user_id = %s
    """, (first_name, last_name, phone, user_id))

    conn.commit()
    cur.close()
    return jsonify({"success": True})

@parent_bp.route('/api/parents/<int:user_id>', methods=['GET'])
def get_single_parent(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.user_id, p.first_name, p.last_name, p.phone, u.email
        FROM parents p JOIN users u ON p.user_id = u.user_id
        WHERE p.user_id = %s
    """, (user_id,))
    row = cur.fetchone()
    cur.close()

    if row:
        return jsonify({
            "user_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "phone": row[3],
            "email": row[4]
        })
    else:
        return jsonify({"error": "Parent not found"}), 404


@parent_bp.route('/api/parents/<int:user_id>', methods=['DELETE'])
def delete_parent(user_id):
    conn = get_db()
    cur = conn.cursor()

    # 🔸 Видаляємо з таблиці parents
    cur.execute("DELETE FROM parents WHERE user_id = %s", (user_id,))

    # 🔸 Видаляємо з таблиці users
    cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))

    conn.commit()
    cur.close()
    return jsonify({"success": True})
