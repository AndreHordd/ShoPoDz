from datetime import datetime, timedelta
from app.models import db, Grade, Lesson, Student, LessonSession

def get_teacher_grades_week(teacher_id, week_start):
    days = []
    if isinstance(week_start, str):
        week_start = datetime.fromisoformat(week_start).date()

    for i in range(7):
        curr_date = week_start + timedelta(days=i)
        dow = curr_date.isoweekday()
        lessons = (
            Lesson.query
            .filter_by(teacher_id=teacher_id, day=dow)
            .order_by(Lesson.start_time)
            .all()
        )
        lesson_items = []
        for L in lessons:
            # Можливо є session на цю дату
            session = LessonSession.query.filter_by(
                lesson_id=L.lesson_id, session_date=curr_date
            ).first()
            grades = []
            if session:
                grades = Grade.query.filter_by(session_id=session.session_id).all()
                session_id = session.session_id
            else:
                session_id = None
            class_size = Student.query.filter_by(class_id=L.class_id).count()
            lesson_items.append({
                'lesson': L,
                'session': session,
                'grades': grades,
                'class_size': class_size,
                'date': curr_date,
                'session_id': session_id
            })
        days.append({'date': curr_date, 'lessons': lesson_items})
    return days

def get_students_in_class(class_id):
    return (
        Student.query
        .filter_by(class_id=class_id)
        .order_by(Student.last_name, Student.first_name)
        .all()
    )

def add_or_update_grade(lesson_id, student_id, teacher_id, value, grade_date, comment=None):
    from app.models import LessonSession
    # 1. Знайти/створити LessonSession на цю дату для цього уроку
    session = LessonSession.query.filter_by(lesson_id=lesson_id, session_date=grade_date).first()
    if not session:
        session = LessonSession(
            lesson_id=lesson_id,
            session_date=grade_date
        )
        db.session.add(session)
        db.session.flush()  # Щоб отримати session_id

    # 2. Додати/оновити оцінку
    g = Grade.query.filter_by(session_id=session.session_id, student_id=student_id).first()
    if g:
        g.grade_value = value
        g.comment = comment
        g.teacher_id = teacher_id
    else:
        g = Grade(
            session_id=session.session_id,
            student_id=student_id,
            teacher_id=teacher_id,
            grade_value=value,
            comment=comment
        )
        db.session.add(g)
    db.session.commit()
    return g
