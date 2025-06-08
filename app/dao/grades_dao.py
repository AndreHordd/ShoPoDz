# app/dao/grades_dao.py

from datetime import datetime, timedelta
from app.models import db, Grade, Lesson, Student


def get_teacher_grades_week(teacher_id, week_start):
    days = []
    if isinstance(week_start, str):
        week_start = datetime.fromisoformat(week_start).date()

    for i in range(7):
        curr = week_start + timedelta(days=i)
        dow  = curr.isoweekday()
        lessons = (Lesson.query
                          .filter_by(teacher_id=teacher_id, day=dow)
                          .order_by(Lesson.start_time)
                          .all())
        lesson_items = []
        for L in lessons:
            grades      = Grade.query.filter_by(lesson_id=L.lesson_id).all()
            # рахуємо кількість учнів цього класу
            class_size  = Student.query.filter_by(class_id=L.class_id).count()
            lesson_items.append({
                'lesson': L,
                'grades': grades,
                'class_size': class_size,
                'date': curr
            })
        days.append({'date': curr, 'lessons': lesson_items})
    return days

def get_students_in_class(class_id):
    """
    Повертає список Student, відсортованих за прізвищем.
    """
    return (Student.query
                  .filter_by(class_id=class_id)
                  .order_by(Student.last_name, Student.first_name)
                  .all())

def add_or_update_grade(lesson_id, student_id, teacher_id, value, comment=None):
    """
    Створює або переписує оцінку.
    """
    g = Grade.query.filter_by(lesson_id=lesson_id, student_id=student_id).first()
    if g:
        g.grade_value = value
        g.comment     = comment
        g.teacher_id  = teacher_id
    else:
        g = Grade(
            lesson_id=lesson_id,
            student_id=student_id,
            teacher_id=teacher_id,
            grade_value=value,
            comment=comment
        )
        db.session.add(g)
    db.session.commit()
    return g
