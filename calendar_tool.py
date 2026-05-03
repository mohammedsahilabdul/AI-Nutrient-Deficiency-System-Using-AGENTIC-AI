from datetime import datetime, timedelta

def add_to_calendar(info):
    appointment_time = datetime.now() + timedelta(days=1)
    return f"📅 Appointment added: {appointment_time.strftime('%Y-%m-%d %H:%M')}"