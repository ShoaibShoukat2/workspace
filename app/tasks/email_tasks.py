"""
Email Background Tasks
"""
from celery import current_task
from app.tasks.celery import celery_app
from app.utils.email import email_service


@celery_app.task(bind=True)
def send_email_task(self, to_email: str, subject: str, html_content: str, text_content: str = None):
    """Send email in background"""
    try:
        success = email_service._send_email_sync(to_email, subject, html_content, text_content)
        if success:
            return {"status": "success", "message": "Email sent successfully"}
        else:
            return {"status": "failed", "message": "Failed to send email"}
    except Exception as exc:
        # Retry task up to 3 times
        if self.request.retries < 3:
            raise self.retry(exc=exc, countdown=60, max_retries=3)
        return {"status": "failed", "message": str(exc)}


@celery_app.task
def send_bulk_emails(email_list: list):
    """Send bulk emails"""
    results = []
    for email_data in email_list:
        result = send_email_task.delay(
            email_data["to_email"],
            email_data["subject"],
            email_data["html_content"],
            email_data.get("text_content")
        )
        results.append(result.id)
    
    return {"status": "queued", "task_ids": results}