from django.core.mail import send_mail
from django.utils import timezone
from .models import FuturePlan

def send_reminders():
    tomorrow = timezone.now().date() + timezone.timedelta(days=1)
    plans = FuturePlan.objects.filter(target_date=tomorrow, email_reminder=True)
    for plan in plans:
        send_mail(
            'Reminder for your future plan',
            f'Remember to: {plan.title} - {plan.description}',
            'aman555bgs@example.com',
            [plan.user.email],
            fail_silently=False,
        )