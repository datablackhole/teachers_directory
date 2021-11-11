from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from directory.models import Teachers, Subjects
import os 

from io import BytesIO
import pandas as pd


import zipfile 
from django.core.files.storage import FileSystemStorage
import time
from django.utils.text import slugify
BASE_PATH_PHOTOS = os.path.join(settings.BASE_DIR, 'media', 'photos')

@login_required
def import_(request):
    if request.method == 'POST':
        if 'zip' in request.FILES:
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
            error_msg = f"{num_left_out} file(s) not imported ! {files_names_left_out}"
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

                return render(request, 'import_.html', {'error_html': error_html})

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

                return render(request, 'import_.html', {'error_html': error_html})

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

                return render(request, 'import_.html', {'error_html': error_html})

            for rec in df.to_dict(orient='records'):
                records_list.append(Teachers(**rec))

            objs = Teachers.objects.bulk_create(records_list)
            success_msg = f"{len(objs)} records have been imported !"

            messages.success(request, success_msg)
            return redirect('home')

    return render(request, 'import_.html', {})

