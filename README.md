# teachers_directory

Requirements:

-> Python 3.7 +

-> Pipenv

-> Git


Instructions to run the applicaion locally:

===================================================================

git clone https://github.com/datablackhole/teachers_directory.git

cd teachers_directory

pip install pipenv

pipenv shell

pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

python manage.py collectstatic

python manage.py runserver 8000


Instructions to use:

===================================================================

-> Use the link http://localhost:8000/ to access the page

-> In order to use the import page you need to register with a valid email address.
