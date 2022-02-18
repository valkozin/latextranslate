web: gunicorn textranslator.wsgi

web: python manage.py runserver 0.0.0.0:\$PORT

web: python manage.py runserver 0.0.0.0:5000





from django.http import HttpResponse
return HttpResponse(str(var))

git push https://git.heroku.com/textranslator.git HEAD:master