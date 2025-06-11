from flask import Blueprint, render_template, session
from app.models import db, Class, Student, ParentSignature
from datetime import datetime, timedelta

signatures_bp = Blueprint('signatures', __name__)

@signatures_bp.route('/teacher/signatures')
def teacher_signatures():
    # Перевірка: лише класний керівник бачить
    teacher_id = session.get('user_id')
    user_role = session.get('role')
    if user_role != 'teacher':
        return render_template('teacher/signatures.html', error="Доступ заборонено")

    # Знайти клас, за який відповідає цей вчитель
    class_ = Class.query.filter_by(class_teacher_id=teacher_id).first()
    if not class_:
        return render_template('teacher/signatures.html', error="Ви не є класним керівником жодного класу!")

    # Знайти учнів цього класу
    students = Student.query.filter_by(class_id=class_.class_id).all()

    # Поточний місяць
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    month_end = next_month

    students_info = []
    for s in students:
        count = ParentSignature.query.filter(
            ParentSignature.student_id == s.user_id,
            ParentSignature.signed_at >= month_start,
            ParentSignature.signed_at < month_end
        ).count()
        students_info.append({
            "student": s,
            "signatures_count": count
        })

    return render_template('teacher/signatures.html',
                           class_=class_,
                           students=students_info,
                           month=now.strftime("%B %Y"),
                           error=None)


