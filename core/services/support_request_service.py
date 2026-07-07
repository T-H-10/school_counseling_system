import logging

from django.conf import settings
from django.core.mail import send_mail

from core.models import SupportRequest

logger = logging.getLogger(__name__)


class SupportRequestService:
    @staticmethod
    def create_request(user, data) -> SupportRequest:
        counselor = user.counselor
        request = SupportRequest.objects.create(
            counselor=counselor,
            school=counselor.school,
            subject=data["subject"],
            message=data["message"],
        )
        subject = f"[מערכת ייעוץ בית ספרי] פנייה חדשה: {request.subject}"
        body = (
            f"יועץ/ת: {counselor.full_name}\n"
            f"בית ספר: {counselor.school.name}\n\n"
            f"{request.message}"
        )
        # The request is already persisted — a failed admin-notification email
        # must not surface to the counselor as a 500. Best-effort send + log.
        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])
        except Exception:
            logger.exception(
                "Failed to send support-request notification email (request id=%s)", request.id
            )
        return request

    @staticmethod
    def resolve_request(request: SupportRequest) -> SupportRequest:
        request.status = SupportRequest.STATUS_RESOLVED
        request.save(update_fields=["status"])
        return request
