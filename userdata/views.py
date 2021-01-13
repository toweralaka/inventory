from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

import string
import random
import requests


# Create your views here.

def send_email(msg, to, subjt, cc=""):
    to = to
    msg = msg
    subjt = subjt
    # cc = "djaafolayan@gmail.com"
    email = EmailMessage(subjt, msg, 'DiamanteMineLimited@mockexamsng.org',
        [to, cc], ['careerinbms@gmail.com',])
    try:
        email.send(fail_silently=False)
    except Exception:
        pass


def send_html_email(msg, html_msg, to, subjt, cc=""):
    to = to
    msg = msg
    html_msg = html_msg
    subjt = subjt
    # cc = "djaafolayan@gmail.com"
    email = EmailMultiAlternatives(subjt, msg, 'DiamanteMineLimited@mockexamsng.org',
        [to, cc], ['careerinbms@gmail.com',])
    email.attach_alternative(html_msg, "text/html")
    try:
        email.send(fail_silently=False)
    except Exception:
        pass
#     subject, from_email, to = 'hello', 'from@example.com', 'to@example.com'
# text_content = 'This is an important message.'
# html_content = '<p>This is an <strong>important</strong> message.</p>'
# msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
# msg.attach_alternative(html_content, "text/html")
# msg.send()




#generate random numbers
def rannum(size, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

#generate random letters
def ranlet(size, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))
