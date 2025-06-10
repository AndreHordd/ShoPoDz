from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app.models import Student, Lesson, User, Teacher

from app.dao.messages_dao import (
    get_teacher_classes,
    get_parents_by_class,
    get_messages_between,
    send_message
)

messages_bp = Blueprint('messenger', __name__, url_prefix='/teacher/messenger')
@messages_bp.route('')
def teacher_messenger():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
    return render_template('teacher/messenger.html')

api_bp = Blueprint('api_messenger', __name__, url_prefix='/api/messenger')

@api_bp.route('/classes')
def api_classes():
    tid = session.get('user_id')
    return jsonify(get_teacher_classes(tid))

@api_bp.route('/parents')
def api_parents():
    class_id = request.args.get('class_id', type=int)
    if not class_id:
        return jsonify([])  # або error
    return jsonify(get_parents_by_class(class_id))

@api_bp.route('/messages/<int:peer_id>')
def api_messages(peer_id):
    me = session.get('user_id')
    return jsonify(get_messages_between(me, peer_id))

@api_bp.route('/send', methods=['POST'])
def api_send():
    data     = request.get_json() or {}
    sender   = session.get('user_id')
    receiver = data.get('receiver_id')
    text     = data.get('text', '').strip()
    if not receiver or not text:
        return jsonify({'error': 'Invalid payload'}), 400
    send_message(sender, receiver, text)
    return jsonify({'status': 'ok'})

# app/api/messages.py  або app/api/messenger_api.py

@api_bp.route('/teachers')
def api_teachers():
    parent_id = session.get('user_id')
    # Знайти учня цього батька
    student = Student.query.filter_by(parent_id=parent_id).first()
    if not student:
        return jsonify([])

    # Знайти всіх унікальних вчителів, які ведуть у цьому класі
    lessons = Lesson.query.filter_by(class_id=student.class_id).all()
    teacher_ids = {l.teacher_id for l in lessons}
    if not teacher_ids:
        return jsonify([])

    teachers = Teacher.query.filter(Teacher.user_id.in_(teacher_ids)).all()
    result = [
        {'id': t.user_id, 'name': f"{t.first_name} {t.last_name}".strip()}
        for t in teachers
    ]
    return jsonify(result)

@messages_bp.route('/parent/messenger')
def parent_messenger():
    if 'user_id' not in session or session.get('role') != 'parent':
        return redirect(url_for('auth.login'))
    return render_template('parent/messenger.html')
