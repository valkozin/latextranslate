web: gunicorn textranslator.wsgi - for Heroku

web: python manage.py runserver 0.0.0.0:\$PORT - for local
web: python manage.py runserver 0.0.0.0:5000


print:
from django.http import HttpResponse
return HttpResponse(str(var))

push to Heroku:
git push https://git.heroku.com/textranslator.git HEAD:master

migrate on Heroku:
Heroku->app->more->Run console
heroku run bash
python manage.py migrate

local:
python manage.py runserver

migrations:
python manage.py makemigrations
python manage.py migrate

git:
git status
git add .
git commit -m "comment"