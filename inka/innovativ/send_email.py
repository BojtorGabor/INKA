# from send_email import send_email
import smtplib, ssl
import os


def send_email(message):
    host = "smtp.gmail.com"
    port = 465
    username = "bojtor.gabor@gmail.com"
    password = os.getenv("PYTHON_PASSWORD")
    receiver = "bojtor.gabor@gmail.com"
    sslcontext = ssl.create_default_context()

#    message = f"""\
#    Subject: New email from {user_email}
#
#    From: {user_email}
#    {your message}
#    """

    with smtplib.SMTP_SSL(host, port, context=sslcontext) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message.encode('utf-8'))