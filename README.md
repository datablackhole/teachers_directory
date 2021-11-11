# teachers_directory

Requirements:

-> Python 3.7 +

-> Pipenv





Instruction to run in development:

git clone https://github.com/datablackhole/teachers_directory.git

cd teachers_directory

pipenv shell

pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

python manage.py collectstatic

python manage.py runserver 8001

