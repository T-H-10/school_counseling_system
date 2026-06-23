from django.conf import settings
from django.core.mail import send_mail

from core.models import SupportRequest


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
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])
        return request

    @staticmethod
    def resolve_request(request: SupportRequest) -> SupportRequest:
        request.status = SupportRequest.STATUS_RESOLVED
        request.save(update_fields=["status"])
        return request
