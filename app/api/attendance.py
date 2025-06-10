
from app.models import db, LessonSession, Lesson, Student, Class, Attendance, Teacher
from datetime import date
from flask import Blueprint, request, jsonify, session, abort, render_template

attendance_bp = Blueprint('attendance_bp', __name__)

# Допоміжна функція отримати user_id вчителя (наприклад, із Flask session)
def get_current_teacher_id():
    teacher_id = session.get('user_id')
    if not teacher_id:
        abort(401)  # Unauthorized
    return teacher_id

@attendance_bp.route('/api/teacher/attendance/sessions', methods=['GET'])
def get_teacher_sessions_by_date():
    date_str = request.args.get('date')
    teacher_id = get_current_teacher_id()
    curr_date = date.fromisoformat(date_str) if date_str else date.today()
    dow = curr_date.isoweekday()  # день тижня

    # Вибираємо лише ті уроки, які мають бути у цей день
    lessons = (
        Lesson.query
        .filter_by(teacher_id=teacher_id, day=dow)
        .join(Class, Lesson.class_id == Class.class_id)
        .order_by(Class.class_number, Class.subclass, Lesson.start_time)
        .all()
    )

    result = []
    for lesson in lessons:
        # Дивимося, чи вже є session для цієї пари на цю дату
        session_obj = LessonSession.query.filter_by(lesson_id=lesson.lesson_id, session_date=curr_date).first()
        _class = lesson.class_
        result.append({
            "session_id": session_obj.session_id if session_obj else None,
            "lesson_id": lesson.lesson_id,
            "class_id": _class.class_id,
            "class_title": f"{_class.class_number}{_class.subclass}",
            "subject": lesson.subject.title,
            "start_time": lesson.start_time.strftime("%H:%M"),
            "end_time": lesson.end_time.strftime("%H:%M"),
        })
    return jsonify(result)

# 2. Всі учні класу з відвідуваністю для цієї сесії
@attendance_bp.route('/api/teacher/attendance/session/<int:session_id>', methods=['GET'])
def get_attendance_for_session(session_id):
    session_obj = LessonSession.query.get_or_404(session_id)
    lesson = session_obj.lesson
    students = (
        Student.query
        .filter_by(class_id=lesson.class_id)
        .order_by(Student.last_name, Student.first_name)
        .all()
    )
    attendance = {a.student_id: a for a in Attendance.query.filter_by(session_id=session_id).all()}
    result = []
    for st in students:
        a = attendance.get(st.user_id)
        result.append({
            "student_id": st.user_id,
            "full_name": f"{st.last_name} {st.first_name}",
            "status": a.status if a else None,
            "comment": a.comment if a else "",
            "attendance_id": a.attendance_id if a else None,
        })
    return jsonify(result)

# 3. Додати/оновити відмітку для учня
@attendance_bp.route('/api/teacher/attendance/mark', methods=['POST'])
def mark_attendance():
    data = request.json
    session_id = data['session_id']
    student_id = data['student_id']
    status = data['status']
    comment = data.get('comment', "")
    # Перевірка, що цей учень дійсно у класі цього уроку
    session_obj = LessonSession.query.get_or_404(session_id)
    lesson = session_obj.lesson
    student = Student.query.get_or_404(student_id)
    if student.class_id != lesson.class_id:
        abort(400, description="Student not in class for this lesson")
    # Запис
    a = Attendance.query.filter_by(session_id=session_id, student_id=student_id).first()
    if a:
        a.status = status
        a.comment = comment
    else:
        a = Attendance(
            session_id=session_id,
            student_id=student_id,
            status=status,
            comment=comment
        )
        db.session.add(a)
    db.session.commit()
    return jsonify({"result": "ok", "attendance_id": a.attendance_id})

# 4. (Необовʼязково) — отримати список дат, на які є уроки у вчителя (для календаря)
@attendance_bp.route('/api/teacher/attendance/active_dates', methods=['GET'])
def get_teacher_active_dates():
    teacher_id = get_current_teacher_id()
    # всі дати, коли є хоча б 1 session у вчителя
    dates = db.session.query(LessonSession.session_date).\
        join(Lesson).filter(Lesson.teacher_id == teacher_id).distinct().all()
    return jsonify([d[0].isoformat() for d in dates])
@attendance_bp.route('/teacher/attendance')
def teacher_attendance():
    return render_template('teacher/teacher_attendance.html')


@attendance_bp.route('/api/teacher/classes', methods=['GET'])
def get_teacher_classes():
    teacher_id = session.get('user_id')
    if not teacher_id:
        return jsonify([])

    # Знаходимо всі класи, де вчитель має уроки
    classes = (
        db.session.query(Class)
        .join(Lesson, Lesson.class_id == Class.class_id)
        .filter(Lesson.teacher_id == teacher_id)
        .distinct()
        .all()
    )
    return jsonify([
        {
            "class_id": c.class_id,
            "class_title": f"{c.class_number}{c.subclass}"
        } for c in classes
    ])
# Додати в class_bp або в attendance_bp:
@attendance_bp.route('/api/classes/<int:class_id>/students', methods=['GET'])
def get_students_for_class(class_id):
    students = Student.query.filter_by(class_id=class_id).order_by(Student.last_name.asc()).all()
    return jsonify([
        {
            "user_id": st.user_id,
            "first_name": st.first_name,
            "last_name": st.last_name
        } for st in students
    ])
@attendance_bp.route('/api/teacher/attendance/create_session', methods=['POST'])
def create_session():
    data = request.json
    lesson_id = data.get('lesson_id')
    date_str = data.get('date')
    if not lesson_id or not date_str:
        return jsonify({'error': 'Не всі поля'}), 400
    session_date = date.fromisoformat(date_str)

    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({'error': 'Урок не знайдено'}), 400
    if lesson.day != session_date.isoweekday():
        return jsonify({'error': 'Цього уроку немає за розкладом у цей день!'}), 400

    session_obj = LessonSession.query.filter_by(lesson_id=lesson_id, session_date=session_date).first()
    if not session_obj:
        session_obj = LessonSession(lesson_id=lesson_id, session_date=session_date)
        db.session.add(session_obj)
        db.session.commit()
    return jsonify({'session_id': session_obj.session_id})
