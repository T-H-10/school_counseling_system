from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.jobstores import DjangoJobStore

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def send_meeting_reminders():
    from datetime import timedelta

    from django.conf import settings
    from django.core.mail import send_mail
    from django.utils import timezone

    from core.models import StudentEvent

    now = timezone.now()
    events = StudentEvent.objects.select_related("counselor__user", "student").filter(
        date__gte=now + timedelta(minutes=25),
        date__lte=now + timedelta(minutes=35),
        reminder_sent=False,
    )
    for event in events:
        recipient = event.counselor.user.email
        if not recipient:
            continue
        subject = f"תזכורת: פגישה עם {event.student.full_name} בעוד 30 דקות"
        body = (
            f"שלום {event.counselor.full_name},\n\n"
            f"תזכורת לפגישה הקרובה:\n\n"
            f"כותרת: {event.title}\n"
            f"תלמיד/ה: {event.student.full_name}\n"
            f"שעה: {event.date.strftime('%H:%M')}\n"
        )
        if event.agenda:
            body += f"\nמטרת הפגישה:\n{event.agenda}\n"
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient])
        event.reminder_sent = True
        event.save(update_fields=["reminder_sent"])


def start():
    scheduler.add_job(
        send_meeting_reminders,
        trigger=IntervalTrigger(minutes=5),
        id="send_meeting_reminders",
        replace_existing=True,
    )
    scheduler.start()
