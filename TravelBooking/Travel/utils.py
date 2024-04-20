# util.py
from django.core.mail import send_mail
from django.conf import settings


def send_email_to_client(subject, message, recipient_list):
    # It's better to use DEFAULT_FROM_EMAIL
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, recipient_list)