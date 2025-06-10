from datetime import datetime, timedelta
from app.models import db, Grade, Lesson, Student, LessonSession

def get_teacher_grades_week(teacher_id, week_start):
    """
    Повертає розклад і всі оцінки за тиждень для вчителя.
    week_start — перший день тижня (date або isoformat str)
    """
    days = []
    if isinstance(week_start, str):
        week_start = datetime.fromisoformat(week_start).date()

    for i in range(7):
        curr_date = week_start + timedelta(days=i)
        # Сесії уроків (LessonSession) цього вчителя на цей день
        sessions = (
            LessonSession.query
            .join(Lesson)
            .filter(Lesson.teacher_id == teacher_id)
            .filter(LessonSession.session_date == curr_date)
            .order_by(Lesson.start_time)
            .all()
        )
        session_items = []
        for session in sessions:
            lesson = session.lesson
            grades = Grade.query.filter_by(session_id=session.session_id).all()
            class_size = Student.query.filter_by(class_id=lesson.class_id).count()
            session_items.append({
                'lesson': lesson,
                'session': session,
                'grades': grades,
                'class_size': class_size,
                'date': curr_date
            })
        days.append({'date': curr_date, 'sessions': session_items})
    return days

def get_students_in_class(class_id):
    """
    Повертає список Student, відсортованих за прізвищем.
    """
    return (
        Student.query
        .filter_by(class_id=class_id)
        .order_by(Student.last_name, Student.first_name)
        .all()
    )

def add_or_update_grade(session_id, student_id, teacher_id, value, comment=None):
    """
    Створює або переписує оцінку (за сесію уроку!).
    """
    g = Grade.query.filter_by(session_id=session_id, student_id=student_id).first()
    if g:
        g.grade_value = value
        g.comment = comment
        g.teacher_id = teacher_id
    else:
        g = Grade(
            session_id=session_id,
            student_id=student_id,
            teacher_id=teacher_id,
            grade_value=value,
            comment=comment
        )
        db.session.add(g)
    db.session.commit()
    return g

def get_grades_for_student(student_id):
    """
    Повертає всі оцінки для даного учня (сортування по даті сесії).
    """
    return (
        Grade.query
        .filter_by(student_id=student_id)
        .join(LessonSession)
        .order_by(LessonSession.session_date)
        .all()
    )
