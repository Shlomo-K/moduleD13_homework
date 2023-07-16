import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from datetime import date, timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from app.models import Notice
from users.models import MyUser


logger = logging.getLogger(__name__)


def weekly_report():
    startDay = date.today() + timedelta(days=-date.today().weekday())
    weekPosts = Notice.objects.filter(Creation_date__gt=startDay)
    Users = MyUser.objects.values(
        'username', 'email').exclude(username='admin')
    postInfo = []

    for post in weekPosts:
        postInfo.append(
            {
                'title': post.Notice_title,
                'author': post.Notice_author.username,
                'date': post.Creation_date,
                'postUrl': str(post.id)
            }
        )

    for Sub in Users:
        html_content = render_to_string(
            'notice/weekly_mail.html',
            {
                'userName': Sub['username'],
                'postInfo': postInfo
            }
        )

        msg = EmailMultiAlternatives(
            subject=f'Еженедельная рассылка',
            from_email='qwerty@gmx.com',
            to=[Sub['email']],
        )
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
        except:
            pass


def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            weekly_report,
            trigger=CronTrigger(
                
                day_of_week="sun", hour="00", minute="00"),
            id="weekly_report",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'weekly_report'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
