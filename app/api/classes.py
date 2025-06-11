from flask import Blueprint, jsonify, request
from app.services.class_service import fetch_all_classes  # або як у тебе називається сервіс
from app.utils.db import get_db
from psycopg2 import errors

class_bp = Blueprint('class', __name__)

@class_bp.route('/api/classes')
def api_get_classes():
    classes = fetch_all_classes()
    return jsonify([
        {
            "id": c["class_id"],
            "name": f"{c['class_number']}-{c['subclass']}",
            "class_number": c["class_number"],
            "subclass": c["subclass"],
            "class_teacher_id": c["class_teacher_id"]  # 🔹 Тепер є
        } for c in classes
    ])

# Створити клас
@class_bp.route('/api/classes', methods=['POST'])
def add_class():
    data = request.get_json()
    class_number = data.get("class_number")
    subclass = data.get("subclass")
    class_teacher_id = data.get("class_teacher_id")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO classes (class_number, subclass, class_teacher_id)
        VALUES (%s, %s, %s)
    """, (class_number, subclass, class_teacher_id))
    conn.commit()
    cur.close()
    return jsonify({"success": True})

# Оновити клас
@class_bp.route('/api/classes/<int:class_id>', methods=['PUT'])
def update_class(class_id):
    data = request.get_json()
    class_number = data.get("class_number")
    subclass = data.get("subclass")
    class_teacher_id = data.get("class_teacher_id")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE classes SET class_number = %s, subclass = %s, class_teacher_id = %s
        WHERE class_id = %s
    """, (class_number, subclass, class_teacher_id, class_id))
    conn.commit()
    cur.close()
    return jsonify({"success": True})

@class_bp.route('/api/classes/<int:class_id>', methods=['DELETE'])
def delete_class(class_id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM classes WHERE class_id = %s", (class_id,))
        conn.commit()
        return jsonify({"success": True})
    except errors.ForeignKeyViolation as e:
        conn.rollback()
        return jsonify({
            "success": False,
            "error": "Неможливо видалити клас, оскільки він має розклад або інших пов’язаних даних."
        }), 400
    except Exception as e:
        conn.rollback()
        return jsonify({
            "success": False,
            "error": "Сталася помилка при видаленні класу."
        }), 500
    finally:
        cur.close()


