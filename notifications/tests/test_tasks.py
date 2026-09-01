from django.test import TestCase, override_settings
from django.core import mail
from notifications.tasks import send_email_task, daily_test_task

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class CeleryTaskTest(TestCase):
    def test_send_email_task(self):
        result = send_email_task.delay(
            'Test Subject',
            'Test Body',
            ['test@example.com']
        )
        self.assertTrue(result.successful())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')

    def test_daily_test_task(self):
        result = daily_test_task.delay()
        self.assertTrue(result.successful())
        self.assertEqual(result.result, 'Daily test task completed')