from app.models import db, Class, Student, Parent, User, Message

def get_teacher_classes(teacher_id):
    from app.models import Lesson, Class
    # всі класи, де є хоча б один lesson з teacher_id
    classes = (
        db.session.query(Class)
        .join(Lesson, Lesson.class_id == Class.class_id)
        .filter(Lesson.teacher_id == teacher_id)
        .distinct()
        .all()
    )
    return [{'class_id': c.class_id, 'title': f"{c.class_number}{c.subclass}"} for c in classes]

def get_parents_by_class(class_id):
    from app.models import Student, Parent
    students = Student.query.filter_by(class_id=class_id).all()
    parent_ids = {s.parent_id for s in students if s.parent_id}

    if not parent_ids:
        return []

    parents = Parent.query.filter(Parent.user_id.in_(list(parent_ids))).all()
    return [
        {'id': p.user_id, 'name': f"{p.first_name} {p.last_name}".strip()}
        for p in parents
    ]

def get_messages_between(user1_id, user2_id):
    msgs = (
        Message.query
          .filter(
            ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
            ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
          )
          .order_by(Message.sent_at)
          .all()
    )
    return [
        {
          'from':    m.sender_id,
          'to':      m.receiver_id,
          'text':    m.text,
          'sentAt':  m.sent_at.isoformat()
        }
        for m in msgs
    ]

def send_message(sender_id, receiver_id, text):
    m = Message(
      sender_id=sender_id,
      receiver_id=receiver_id,
      text=text
    )
    db.session.add(m)
    db.session.commit()
