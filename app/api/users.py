from flask import Blueprint, jsonify, request
from app.dao.user_dao import UserDAO

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


@users_bp.route('/init-db', methods=['POST'])
def init_database():
    """Ініціалізує таблицю users"""
    try:
        UserDAO.create_table()
        return jsonify({"message": "Таблиця users створена успішно"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route('/', methods=['GET'])
def get_users():
    """Отримує всіх користувачів"""
    try:
        users = UserDAO.get_all_users()
        return jsonify([{
            'id': u.id,
            'username': u.username,
            'email': u.email
        } for u in users]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route('/', methods=['POST'])
def create_user():
    """Створює нового користувача"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        
        if not username or not email:
            return jsonify({"error": "Username та email обов'язкові"}), 400
        
        user = UserDAO.create_user(username, email)
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
