# app/dao/homework_dao.py

from datetime import datetime, timedelta
from app.models import db, Homework, Lesson

# app/dao/homework_dao.py

from datetime import datetime, timedelta
from sqlalchemy import func
from app.models import db, Homework, Lesson

def get_teacher_homework_week(teacher_id, week_start):
    if isinstance(week_start, str):
        week_start = datetime.fromisoformat(week_start).date()

    week = []
    for offset in range(7):
        curr_date = week_start + timedelta(days=offset)
        dow = curr_date.isoweekday()  # 1=Понеділок … 7=Неділя

        lessons = Lesson.query.filter_by(
            teacher_id=teacher_id,
            day=dow
        ).order_by(Lesson.start_time, Lesson.class_id).all()

        lessons_data = []
        for lesson in lessons:
            # Ось тут ми фільтруємо вже по даті дедлайну, а не просто по lesson_id:
            hw = Homework.query.filter(
                Homework.lesson_id == lesson.lesson_id,
                func.date(Homework.deadline) == curr_date
            ).first()
            lessons_data.append({
                "lesson": lesson,
                "homework": hw,
                "date": curr_date
            })

        week.append({
            "date": curr_date,
            "lessons": lessons_data
        })

    return week

# app/dao/homework_dao.py

from datetime import datetime
from app.models import db, Homework, Lesson
# app/dao/homework_dao.py

from datetime import datetime, date
from app.models import db, Homework, Lesson

def add_homework(lesson_id, description, deadline):
    """
    Якщо для lesson_id вже є Homework — оновити його,
    інакше створити новий.
    """
    # 1) Парсимо deadline
    if isinstance(deadline, str):
        try:
            deadline = datetime.fromisoformat(deadline)
        except ValueError:
            return False, "Невірний формат дати дедлайну"

    # 2) Шукаємо урок
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return False, "У цей день у вас немає уроків"

    # 3) Перевіряємо, що дедлайн відповідає дню уроку
    if deadline.date().isoweekday() != lesson.day:
        return False, "У цей день у вас немає уроків"

    # 4) Заборона дедлайну в минулому
    if deadline.date() < date.today():
        return False, "Неможливо задати дедлайн у минулому"

    # 5) Перевіряємо, чи вже є Homework для цього уроку
    existing = Homework.query.filter_by(lesson_id=lesson_id).first()
    if existing:
        # просто перезаписуємо опис і дедлайн
        existing.description = description
        existing.deadline = deadline
        db.session.commit()
        return True, existing

    # 6) Якщо нема — створюємо нове
    hw = Homework(
        lesson_id=lesson_id,
        description=description,
        deadline=deadline
    )
    db.session.add(hw)
    db.session.commit()
    return True, hw

def update_homework(homework_id, description, deadline):
    """
    Оновлює домашнє завдання.
    Повертає (True, hw) або (False, повідомлення).
    """
    if isinstance(deadline, str):
        try:
            deadline = datetime.fromisoformat(deadline)
        except ValueError:
            return False, "Невірний формат дати дедлайну"

    hw = Homework.query.get(homework_id)
    if not hw:
        return False, "Домашнє завдання не знайдено"

    # Перевіряємо, щоб дедлайн відповідав дню уроку
    lesson = Lesson.query.get(hw.lesson_id)
    if deadline.date().isoweekday() != lesson.day:
        return False, "У цей день у вас немає уроків"

    from datetime import date
    if deadline.date() < date.today():
        return False, "Неможливо задати дедлайн у минулому"

    hw.description = description
    hw.deadline = deadline
    db.session.commit()
    return True, hw


def delete_homework(homework_id):
    """
    Видаляє домашнє завдання з БД.
    Повертає (True, None) або (False, помилка).
    """
    hw = Homework.query.get(homework_id)
    if not hw:
        return False, "Домашнє завдання не знайдено"

    if hw.deadline.date() < datetime.today().date():
        return False, "Неможливо видалити ДЗ із дедлайном у минулому"

    db.session.delete(hw)
    db.session.commit()
    return True, None
