from django.shortcuts import render
from django.core.mail import send_mail
from django.http import HttpResponse


def send_email(subject, message, to_email):
    sent = send_mail(subject, message, to_email)

    if sent:
        return HttpResponse('E-mail sikeresen elküldve!')
    else:
        return HttpResponse('Hiba történt az e-mail küldése közben!')