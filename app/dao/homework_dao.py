from app.models import Homework, Lesson
from app import db
from datetime import datetime

from datetime import datetime, timedelta

def get_teacher_homework_week(teacher_id, week_start):
    """
    week_start — це понеділок календарного тижня (date obj або isoformat str)
    """
    if isinstance(week_start, str):
        week_start = datetime.fromisoformat(week_start).date()
    lessons_by_day = []
    for i in range(7):
        curr_date = week_start + timedelta(days=i)
        day_of_week = curr_date.isoweekday()  # 1=Monday, ..., 7=Sunday
        # Всі уроки цього вчителя в цей день тижня
        lessons = Lesson.query.filter(
            Lesson.teacher_id == teacher_id,
            Lesson.day == day_of_week
        ).order_by(Lesson.start_time, Lesson.class_id).all()
        # Для кожного уроку шукай дз (по lesson_id)
        day_lessons = []
        for lesson in lessons:
            hw = Homework.query.filter_by(lesson_id=lesson.lesson_id).first()
            day_lessons.append({
                "lesson": lesson,
                "homework": hw,
                "date": curr_date  # щоб знати дату відображення
            })
        lessons_by_day.append({
            "date": curr_date,
            "lessons": day_lessons
        })
    return lessons_by_day

def add_homework(lesson_id, description, deadline):
    lesson = Lesson.query.get(lesson_id)
    if not lesson or lesson.date < datetime.today().date():
        return False, "Cannot add homework for past lesson"
    hw = Homework(
        lesson_id=lesson_id,
        description=description,
        deadline=deadline
    )
    db.session.add(hw)
    db.session.commit()
    return True, hw

def update_homework(homework_id, description, deadline):
    hw = Homework.query.get(homework_id)
    if not hw:
        return False, "Homework not found"
    lesson = Lesson.query.get(hw.lesson_id)
    if lesson.date < datetime.today().date():
        return False, "Cannot edit homework for past lesson"
    hw.description = description
    hw.deadline = deadline
    db.session.commit()
    return True, hw

def delete_homework(homework_id):
    hw = Homework.query.get(homework_id)
    if not hw:
        return False, "Homework not found"
    lesson = Lesson.query.get(hw.lesson_id)
    if lesson.date < datetime.today().date():
        return False, "Cannot delete homework for past lesson"
    db.session.delete(hw)
    db.session.commit()
    return True, None
