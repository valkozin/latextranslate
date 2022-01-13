from django.http import HttpResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .forms import DocumentForm
import json
import os
import sys
sys.path.append('textranslator/latextranslator-master')
# import main.py
from shutil import copyfile
import requests
import urllib.request

# Create your views here.
# def index(request):
#     if request.method == 'POST' and request.FILES['myfile']:
#         # myfile = request.FILES['myfile']
#         # fs = FileSystemStorage()
#         # filename = fs.save(myfile.name, myfile)
#         # uploaded_file_url = fs.url(filename)
#         # return render(request, 'main_app/index.html', {
#         #     'uploaded_file_url': uploaded_file_url
#         # })
#         #
#         # Заполняем форму полученными данными
#         form = UploadFileForm(request.POST, request.FILES)
#         # Если данные валидны
#         if form.is_valid():
#             # обрабатываем файл
#             handle_uploaded_file(request.FILES['file'])
#     return render(
#         request,
#         'main_app/index.html',
#         context={},
#     )


def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            check_error = 0

            allowed = []
            allowed.append('tex')

            filename, file_extension = os.path.splitext('documents/'+request.FILES['document'].name)
            if file_extension not in allowed:
                check_error = 1

            if os.stat('documents/'+request.FILES['document'].name).st_size > 1048576:
                check_error = 2

            copyfile(os.path.dirname(os.path.abspath(__file__)) + "/../documents/"+request.FILES['document'].name,
                     os.path.dirname(os.path.abspath(__file__)) + "/../latextranslator-master/examples/" +
                     request.FILES['document'].name)

            response = os.system("python " +
                os.path.dirname(os.path.abspath(__file__)) + "/../latextranslator-master/main.py " +
                os.path.dirname(os.path.abspath(__file__)) + "/../latextranslator-master/examples/" + request.FILES['document'].name + " ru")

            # url = 'https://www.facebook.com/favicon.ico'
            # r = requests.get(url, allow_redirects=True)
            #
            # open('facebook.ico', 'wb').write(r.content)

            # with urllib.request.urlopen('http://http://127.0.0.1:8000/main_app/') as f:
            #     html = f.read().decode('utf-8')

            content = open(os.path.dirname(os.path.abspath(__file__))+"/../latextranslator-master/examples/" + request.FILES['document'].name + " ru", encoding="utf8").read()

            response = HttpResponse(content, 'rb')
            response['Content-Type'] = 'text/plain'
            response['Content-Disposition'] = 'attachment;'
            return response
            # return HttpResponse(content, content_type='text/plain')

            # print(r"C:\Users\DariaKhudiakova\PycharmProjects\textranslator\latextranslator-master\main.py C:\Users\DariaKhudiakova\PycharmProjects\textranslator\latextranslator-master\examples\test_Dasha.tex ru")
            # response = os.system(
            #     r"python C:\Users\DariaKhudiakova\PycharmProjects\textranslator\latextranslator-master\main.py C:\Users\DariaKhudiakova\PycharmProjects\textranslator\latextranslator-master\examples\test_Dasha.tex ru")

            # print(response)
            # response = json.dumps(value)

            # return redirect('home')
    else:
        form = DocumentForm()
    return render(request, 'main_app/index.html', {
        'form': form,
        # 'response': response
    })
