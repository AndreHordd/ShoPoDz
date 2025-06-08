from app.models import Attendance

def get_attendance_for_student(student_id: int):
    """
    Повертає список об’єктів Attendance для даного учня.
    Кожен має, щонайменше, поля status і, якщо є, дату запису.
    """
    return Attendance.query.filter_by(student_id=student_id).order_by(Attendance.attendance_id).all()
