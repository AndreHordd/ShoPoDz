from flask import Blueprint, jsonify
from app.services.class_service import fetch_all_classes  # або як у тебе називається сервіс

class_bp = Blueprint('class', __name__)

@class_bp.route('/api/classes')
def api_get_classes():
    classes = fetch_all_classes()
    return jsonify([
        {
            "id": c.class_id,
            "name": f"{c.class_number}-{c.subclass}",
            "class_number": c.class_number  # 🔥 Додай це!
        } for c in classes
    ])

