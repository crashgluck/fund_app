from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_admin_email(subject, message, recipient_list):
    """Envía un correo electrónico al administrador cuando hay un registro nuevo pendiente."""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        return f"Correo enviado a {recipient_list}"
    except Exception as e:
        return f"Error enviando correo: {str(e)}"
