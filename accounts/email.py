from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives 
from django.utils.html import strip_tags

import threading
class EmailThread(threading.Thread):
    def __init__(self, subject, content, sender,recipient_list):
        self.subject = subject
        self.content = content
        self.recipient_list = recipient_list
        self.sender = sender
        threading.Thread.__init__(self)
    def run(self):
        plain_message = strip_tags(self.content)
        send_mail(self.subject, plain_message , self.sender, self.recipient_list, html_message=self.content,fail_silently=True,)
        

class EmailMultiAlternativesThread(threading.Thread):
    def __init__(self, subject, content, from_email, to, cc):
        self.subject = subject
        self.content = content
        self.to = to
        self.from_email = from_email
        self.cc = cc
        threading.Thread.__init__(self)
    def run(self):
        plain_message = strip_tags(self.content)
        # send_mail(self.subject, plain_message , self.sender, self.to, html_message=self.content,fail_silently=True,)
        mail = EmailMultiAlternatives(self.subject, plain_message, self.from_email, self.to, cc=self.cc)
        if self.content:
            mail.attach_alternative(self.content, 'text/html')
        mail.send()

        

class EmailMultiAlternativesWithAttachmentsThread(threading.Thread):
    def __init__(self, subject, content, from_email, to, cc,attachments):
        self.subject = subject
        self.content = content
        self.to = to
        self.from_email = from_email
        self.cc = cc
        self.attachments = attachments
        threading.Thread.__init__(self)
    def run(self):
        plain_message = strip_tags(self.content)
        # send_mail(self.subject, plain_message , self.sender, self.to, html_message=self.content,fail_silently=True,)
        mail = EmailMultiAlternatives(self.subject, plain_message, self.from_email, self.to, cc=self.cc)
        if self.content:
            mail.attach_alternative(self.content, 'text/html')
        if self.attachments:
            for _file_ in self.attachments:
                mail.attach(_file_['file_name'], _file_['content'], _file_['mime_type'])
        mail.send()

        


def send_async_mail_cc(subject, content, sender,to,cc):
    EmailMultiAlternativesThread(subject, content, sender,to,cc).start()

def send_async_mail_cc_attachments(subject, content, sender,to,cc,attachments):
    EmailMultiAlternativesWithAttachmentsThread(subject, content, sender,to,cc,attachments).start()


def send_async_mail(subject, content, sender,recipient_list):
    EmailThread(subject, content, sender,recipient_list).start()
