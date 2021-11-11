
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string

from django.core.validators import validate_email
from django.contrib.auth.models import User

from django.http import Http404
from .email import send_async_mail


MIN_PASSWORD_LENGTH = 6


# Create your views here.
def login(request):
    redirect_page = request.GET.get('next', '')
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            if redirect_page != '':
                return redirect(redirect_page)

            return redirect('home')
        else:
            messages.error(request, 'Incorrect Username or Password')
            return redirect('login')


    if 'import' in redirect_page:
        messages.info(request, ': Please Log In or Register to access importer!')




    return render(request, 'login.html', {})

def logout(request):
    auth.logout(request)
    messages.success(request, 'You are now logged out')
    return redirect('home')

def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        repassword = request.POST['repassword']

        try:
            validate_email(email)
        except ValidationError as e:
            messages.error(request, 'Email invalid !')
            return redirect('register')

        if password != repassword:
            messages.error(request, 'Passwords do not match !')
            return redirect('register')

        if len(password) < MIN_PASSWORD_LENGTH:
            messages.error(request, f'Minimum password length is {MIN_PASSWORD_LENGTH} characters !')
            return redirect('register')

        else:
            # Check username
            if User.objects.filter(username=email).exists():
                messages.error(request, 'That username is taken')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'That email is being used')
                return redirect('register')

            token = settings.CIPHER_SUITE.encrypt(str.encode(email)).decode('utf-8')
            user = User.objects.create_user(username=email, password=password, email=email, is_active=False)
            print(user)
            user.save()
            print(user)


            http_reffer = request.META['HTTP_REFERER']
            email_subject = 'Click to verify email'
            email_context = {}
            email_context['http_reffer'] = http_reffer
            email_context['token'] = token
            email_body = render_to_string('email/verify_email.html', email_context)

            send_async_mail(
                email_subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
            messages.success(request,
                             'Please check your email inbox or spam folder for the link to verify your account')
            return redirect('login')

    return render(request, 'register.html', {})

def register_verify(request):
    verification_token = request.GET.get('token', "")

    if verification_token == "":
        raise Http404

    email = settings.CIPHER_SUITE.decrypt(str.encode(verification_token)).decode('utf-8')

    User.objects.filter(username=email).update(is_active=True)

    messages.success(request, 'Email successfully verified! You may now login.')
    return redirect('login')
