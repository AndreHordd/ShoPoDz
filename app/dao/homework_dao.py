from datetime import datetime, date, timedelta
from app.models import db, Lesson, LessonSession, Homework

def get_teacher_homework_week(teacher_id, week_start):
    """
    Повертає список днів тижня з розкладом уроків і домашками вчителя.
    Для кожного уроку на кожний день шукає LessonSession і Homework.
    """
    week = []
    for offset in range(7):
        curr_date = week_start + timedelta(days=offset)
        dow = curr_date.isoweekday()  # 1=Понеділок … 7=Неділя

        # Шукаємо всі уроки вчителя на цей день
        lessons = (
            Lesson.query
            .filter_by(teacher_id=teacher_id, day=dow)
            .order_by(Lesson.start_time, Lesson.class_id)
            .all()
        )

        lessons_data = []
        for lesson in lessons:
            # Шукаємо сесію (LessonSession) для цієї пари і дати
            session = (
                LessonSession.query
                .filter_by(lesson_id=lesson.lesson_id, session_date=curr_date)
                .first()
            )
            # Якщо сесія є, шукаємо домашку
            homework = None
            if session:
                homework = Homework.query.filter_by(session_id=session.session_id).first()
            lessons_data.append({
                "lesson": lesson,
                "session": session,
                "homework": homework,
                "date": curr_date
            })

        week.append({
            "date": curr_date,
            "lessons": lessons_data
        })

    return week


def add_homework(teacher_id, class_id, subject_id, description, deadline):
    """
    Додає або оновлює домашнє завдання для конкретної сесії уроку (LessonSession).
    Якщо сесія для цієї дати і уроку не існує — повертає помилку.
    """
    if isinstance(deadline, str):
        try:
            deadline = datetime.fromisoformat(deadline)
        except ValueError:
            return False, "Невірний формат дати дедлайну"

    # Знаходимо Lesson саме для дня дедлайну
    lesson = (
        Lesson.query
        .filter_by(
            teacher_id=teacher_id,
            class_id=class_id,
            subject_id=subject_id,
            day=deadline.date().isoweekday()
        )
        .first()
    )
    if not lesson:
        return False, "У цей день у вас немає цього уроку"

    # Забороняємо дедлайн у минулому
    if deadline.date() < date.today():
        return False, "Неможливо задати дедлайн у минулому"

    # Шукаємо сесію уроку на цю дату
    session = LessonSession.query.filter_by(
        lesson_id=lesson.lesson_id,
        session_date=deadline.date()
    ).first()
    if not session:
        return False, "У цей день у вас немає цього уроку (немає сесії)"

    # Перевіряємо, чи вже є Homework для цієї сесії
    existing = Homework.query.filter_by(session_id=session.session_id).first()
    if existing:
        existing.description = description
        existing.deadline = deadline
        db.session.commit()
        return True, existing

    hw = Homework(
        session_id=session.session_id,
        description=description,
        deadline=deadline
    )
    db.session.add(hw)
    db.session.commit()
    return True, hw

def update_homework(homework_id, description, deadline):
    """
    Оновлює домашнє завдання.
    """
    if isinstance(deadline, str):
        try:
            deadline = datetime.fromisoformat(deadline)
        except ValueError:
            return False, "Невірний формат дати дедлайну"

    hw = Homework.query.get(homework_id)
    if not hw:
        return False, "Домашнє завдання не знайдено"

    session = LessonSession.query.get(hw.session_id)
    if deadline.date() != session.session_date:
        return False, "Дедлайн не відповідає даті проведення уроку"

    hw.description = description
    hw.deadline = deadline
    db.session.commit()
    return True, hw

def delete_homework(homework_id):
    """
    Видаляє домашнє завдання.
    """
    hw = Homework.query.get(homework_id)
    if not hw:
        return False, "Домашнє завдання не знайдено"
    db.session.delete(hw)
    db.session.commit()
    return True, None
