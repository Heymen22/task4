import logging
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)

_scheduler = None


def check_expiring_rentals():
    from .models import Book, Notification, Rental, RentalReminder

    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

    expiring = Rental.objects.filter(
        status=Rental.STATUS_ACTIVE,
        end_date__lte=tomorrow,
        reminder_sent=False,
    ).select_related('user', 'book')

    for rental in expiring:
        message = (
            f'Напоминание: срок аренды книги «{rental.book.title}» '
            f'истекает {rental.end_date.strftime("%d.%m.%Y")}. '
            f'Пожалуйста, верните книгу вовремя.'
        )

        if rental.user.email:
            send_mail(
                subject='Напоминание об окончании аренды',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[rental.user.email],
                fail_silently=True,
            )
            RentalReminder.objects.create(
                rental=rental,
                message=message,
                channel=RentalReminder.CHANNEL_EMAIL,
            )

        Notification.objects.create(user=rental.user, message=message)
        RentalReminder.objects.create(
            rental=rental,
            message=message,
            channel=RentalReminder.CHANNEL_IN_APP,
        )

        rental.reminder_sent = True
        rental.save(update_fields=['reminder_sent'])

    overdue = Rental.objects.filter(
        status=Rental.STATUS_ACTIVE,
        end_date__lt=today,
    ).select_related('book')

    for rental in overdue:
        rental.status = Rental.STATUS_OVERDUE
        rental.save(update_fields=['status'])
        rental.book.status = Book.STATUS_AVAILABLE
        rental.book.save(update_fields=['status'])

    if expiring or overdue:
        logger.info(
            'Rental check: %d reminders sent, %d overdue processed',
            len(expiring),
            len(overdue),
        )


def start_scheduler():
    global _scheduler
    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    _scheduler.add_job(
        check_expiring_rentals,
        trigger='interval',
        hours=1,
        id='check_expiring_rentals',
        replace_existing=True,
    )
    _scheduler.start()
    logger.info('APScheduler started: rental reminder job every 1 hour')
