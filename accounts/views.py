from django.contrib.messages.api import error, success
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth
from django.conf import settings
from django.http import JsonResponse
from .email import send_async_mail
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string

from django.core.validators import validate_email
from django.contrib.auth.models import User
from .models import UserProfile
from django.http import Http404
from .models import Teachers, Subjects
import os

from io import BytesIO
import pandas as pd

MIN_PASSWORD_LENGTH = 6


# Create your views here.
def login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            redirect_page = request.GET.get('next', '')
            if redirect_page != '':
                return redirect(redirect_page)

            return redirect('home')
        else:
            messages.error(request, 'Incorrect Username or Password')
            return redirect('login')

    return render(request, 'login.html', {})


def logout(request):
    auth.logout(request)
    messages.success(request, 'You are now logged out')
    return redirect('home')


def search(request):
    context = list(
        Subjects.objects.filter(subject_name__icontains=request.GET['term']).order_by('subject_name').values())

    return JsonResponse(context, safe=False, )


from django.core.paginator import Paginator


def home(request):
    context = {}

    queryset_list = Teachers.objects.order_by('first_name')
    term = request.GET.get('term', '')

    query_filter = {}

    if 'filter' in request.GET:
        if request.GET['filter'] == 'ln':
            query_filter['last_name__istartswith'] = term
        elif request.GET['filter'] == 'subject':
            query_filter['subjects_taught__icontains'] = term
        queryset_list = queryset_list.filter(**query_filter)

    paginator = Paginator(queryset_list, 10)  # Show 5 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context['page_obj'] = page_obj

    queryset_list = list(page_obj.object_list.values())
    # print(queryset_list)

    """
        Checking if profile picture exists with respect to filename
    """
    for teacher in queryset_list:
        path = os.path.join(settings.BASE_DIR, 'media', 'photos', teacher['profile_picture'])
        print(path)
        if os.path.exists(path):
            print()
            teacher['picture_exists'] = True
        else:
            teacher['picture_exists'] = False

    # stop 

    comp_context = {'teachers': queryset_list}
    teachers_html = render_to_string('components/teacher_card.html', comp_context)

    if request.is_ajax():
        return HttpResponse(teachers_html)

    context['teachers_html'] = teachers_html

    context['values'] = request.GET

    return render(request, 'home.html', context)

import zipfile 
from django.core.files.storage import FileSystemStorage
import time
from django.utils.text import slugify

@login_required
def import_(request):
    if request.method == 'POST':
        if 'zip' in request.FILES:
            BASE_PATH_PHOTOS = os.path.join(settings.BASE_DIR, 'media', 'photos')
            fs = FileSystemStorage(location=BASE_PATH_PHOTOS)

            zip_file = request.FILES.get('zip')
            with zipfile.ZipFile(zip_file, 'r') as z:
                num = len(z.namelist())
                for f in z.namelist():
                    image_file = z.read(name=f)
                    image_file_name =f.lower()
                    files_names_left_out = []
                    if image_file_name.endswith('.jpg') or  image_file_name.endswith('.jpeg') or  image_file_name.endswith('.png'):
                        image_path =  os.path.join(settings.BASE_DIR, 'media', 'photos',image_file_name)
                        print(image_path)
                        if (os.path.exists(image_path)):
                            new_file_name = slugify(time.ctime() + image_file_name)
                            new_bkup_path = os.path.join(BASE_PATH_PHOTOS,new_file_name)
                            os.rename(image_path,new_bkup_path)
                        file = fs.save(image_file_name,BytesIO(image_file))
                        fileurl = fs.url(file)
                        print(fileurl)
                    
                    else:
                        files_names_left_out.append(image_file_name)


            # stp
            num_left_out =len(files_names_left_out)
            num_of_images_uploaded = num -num_left_out
            success_msg = f"{num_of_images_uploaded} profile images have been imported !"
            messages.success(request, success_msg)

            files_names_left_out = ",".join(files_names_left_out)
            error_msg = f"{num_left_out} files have not been imported ! {files_names_left_out}"
            messages.error(request, error_msg)
            return redirect('home')

        if 'csv' in request.FILES:
            csv = request.FILES.get('csv')
            df = pd.read_csv(BytesIO(csv.read())).fillna("")

            for col in list(df):
                df[col] = df[col].str.strip()

            records_list = []
            df.columns = [
                'first_name',
                'last_name',
                'profile_picture',
                'email_address',
                'phone_number',
                'room_number',
                'subjects_taught',
            ]

            df = df[df['email_address'] != ""]

            # Validation 1: Five Subjects only
            df_invalid = pd.DataFrame(columns=df.columns)

            num_of_subjects = df['subjects_taught'].apply(lambda x: len(x.split(","))).tolist()
            print(num_of_subjects)
            for num, i in zip(num_of_subjects, range(len(num_of_subjects))):
                if num > 5:
                    print(df.iloc[i])
                    df_invalid = pd.concat([df_invalid, df.iloc[i].to_frame().T])

            print(df_invalid)

            if not df_invalid.empty:
                df_invalid.columns = [" ".join([c.title() for c in col.split("_")]) for col in list(df_invalid)]
                df_invalid.index = df_invalid.index + 2
                error_html = df_invalid.to_html(classes=['table table-sm text-nowrap '])
                messages.error(request, 'Following records have subjects greater than 5 !')

                return render(request, 'import_contacts.html', {'error_html': error_html})

            # Initcapping Subject Names
            df['subjects_taught'] = df['subjects_taught'].apply(
                lambda
                    subjects:
                ",".join(
                    [
                        " ".join([name.title() for name in subject.split(" ")]).strip()  # ' sub name2' to 'Sub Name2'
                        for subject in subjects.split(",")  # "sub name1, sub name2" to ['sub name1',' sub name2']
                    ]
                )
            )

            subjects_taught = df['subjects_taught'].tolist()
            all_subjects = set()
            for sub in subjects_taught:
                all_subjects.update(sub.split(","))

            print(all_subjects)

            for sub in all_subjects:
                if Subjects.objects.filter(subject_name=sub).exists() == False:
                    Subjects(subject_name=sub).save()

            email_list = df['email_address'].tolist()

            # Email duplicate check in uploaded
            df_invalid = pd.DataFrame(columns=df.columns)

            for email, i in zip(email_list, range(len(email_list))):

                if (df[df['email_address'] == email].shape[0] > 1):
                    df_invalid = pd.concat([df_invalid, df.iloc[i].to_frame().T])

            if not df_invalid.empty:
                df_invalid.columns = [" ".join([c.title() for c in col.split("_")]) for col in list(df_invalid)]
                df_invalid.index = df_invalid.index + 2
                error_html = df_invalid.to_html(classes=['table table-sm text-nowrap '])
                messages.error(request, 'Following email addressess are repeating  !')

                return render(request, 'import_contacts.html', {'error_html': error_html})

            # Email duplicate check in database
            df_invalid = pd.DataFrame(columns=df.columns)

            for email, i in zip(email_list, range(len(email_list))):
                if Teachers.objects.filter(email_address__iexact=email).exists():
                    df_invalid = pd.concat([df_invalid, df.iloc[i].to_frame().T])

            if not df_invalid.empty:
                df_invalid.columns = [" ".join([c.title() for c in col.split("_")]) for col in list(df_invalid)]
                df_invalid.index = df_invalid.index + 2
                error_html = df_invalid.to_html(classes=['table table-sm text-nowrap '])
                messages.error(request, 'Records with following email addressess have already been imported  !')

                return render(request, 'import_contacts.html', {'error_html': error_html})

            for rec in df.to_dict(orient='records'):
                records_list.append(Teachers(**rec))

            objs = Teachers.objects.bulk_create(records_list)
            success_msg = f"{len(objs)} records have been imported !"

            messages.success(request, success_msg)
            return redirect('home')

    return render(request, 'import_.html', {})


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

            profile = UserProfile(
                user_id=user.pk,
                email_verification_token=token
            )
            profile.save()

            # UserProfile.objects.get(pk=user.pk).update()
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

def teacher(request,id):
    print(id)
    context = {}
    try:
        teacher = Teachers.objects.get(pk=id).__dict__
        del teacher['_state']
        context['profile_picture'] = teacher.pop('profile_picture')
        path = os.path.join(settings.BASE_DIR, 'media', 'photos', context['profile_picture'])
        context['picture_exists'] = os.path.exists(path)
        del teacher['id']
        for key in list(teacher):
            newKey = " ".join([e.title() for e in key.split('_')])
            teacher[newKey] = teacher.pop(key)
        context['teacher'] = teacher
    except:
        raise Http404
    return render(request, 'teacher.html', context)

def register_verify(request):
    verification_token = request.GET.get('token', "")

    if verification_token == "":
        raise Http404

    email = settings.CIPHER_SUITE.decrypt(str.encode(verification_token)).decode('utf-8')

    User.objects.filter(username=email).update(is_active=True)

    messages.success(request, 'Email successfully verified! You may now login.')
    return redirect('login')
