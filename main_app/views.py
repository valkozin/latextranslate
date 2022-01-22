from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage

# from textranslator.settings import DEFAULT_FILE_STORAGE
from . import basic, latex
from .forms import DocumentForm
import json
import os
import sys
# sys.path.append('textranslator/latextranslator-master')
# import main.py
from shutil import copyfile
import requests
import urllib.request
from .models import DocumentTex
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.core.files.storage import default_storage

# trans
import argparse
import os

import regex
import sys
import pickle

from django.http import HttpResponse

import main_app.basic  # Interface to basic Google translation API
import main_app.latex  # LaTeX tokenizer

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


class DocumentCreateView(CreateView):
    model = DocumentTex
    fields = ['upload', ]
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        documents = DocumentTex.objects.all()
        context['documents'] = documents
        return context


def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            check_error = 0

            allowed = []
            allowed.append('tex')

            # filename, file_extension = os.path.splitext(request.FILES['document'].name)
            filename, file_extension = os.path.splitext(request.FILES['upload'].name)
            if file_extension not in allowed:
                check_error = 1

            # if os.stat('documents/'+request.FILES['upload'].name).st_size > 1048576:
            #     check_error = 2

            # copyfile(os.path.dirname(os.path.abspath(__file__)) + "/../documents/"+request.FILES['upload'].name,
            #          os.path.dirname(os.path.abspath(__file__)) + "/../latextranslator-master/examples/" +
            #          request.FILES['upload'].name)

            # response = os.system("python " +
            #     os.path.dirname(os.path.abspath(__file__)) + "/../latextranslator-master/main.py " +
            #     os.path.dirname(os.path.abspath(__file__)) + "/../latextranslator-master/examples/" + request.FILES['upload'].name + " ru")

            # response = HttpResponse("python " +
            #                      os.path.dirname(os.path.abspath(__file__)) + "/../latextranslator-master/main.py " +
            #                      'https://textranslate.s3.eu-west-2.amazonaws.com/' + 'documents/' + request.FILES['upload'].name + " ru")
            # return response
            # response = os.system("python " +
            #                      os.path.dirname(os.path.abspath(__file__)) + "/../latextranslator-master/main.py " +
            #                      default_storage.url(request.FILES['upload'].name) + " ru")


            # response = os.system("python " +
            #                      os.path.dirname(os.path.abspath(__file__)) + "/../latextranslator-master/main.py " +
            #                      'https://textranslate.s3.eu-west-2.amazonaws.com/' + 'documents/' + request.FILES['upload'].name + " ru")
            # return response

            # translate(default_storage.open('documents/' + request.FILES['upload'].name).read(), 'ru')
            translate(default_storage.url('documents/' + request.FILES['upload'].name), request.FILES['upload'].name, 'ru')

            # url = 'https://www.facebook.com/favicon.ico'
            # r = requests.get(url, allow_redirects=True)
            #
            # open('facebook.ico', 'wb').write(r.content)

            # with urllib.request.urlopen('http://http://127.0.0.1:8000/main_app/') as f:
            #     html = f.read().decode('utf-8')

            # content = open(os.path.dirname(os.path.abspath(__file__))+"/../latextranslator-master/examples/" + filename + "_ru" + file_extension, encoding="utf8").read()
            # content = open(default_storage.url(filename + file_extension),
            #                encoding="utf8").read()

            # return HttpResponse(str(filename))
            # return HttpResponse(str(default_storage.url('/documents/' + filename + file_extension)))


            # content = default_storage.open('documents/' + filename + file_extension, 'r')
            #
            # response = HttpResponse(content, 'rb')
            # response['Content-Type'] = 'text/plain'
            # response['Content-Disposition'] = 'attachment;'
            # return response

            content = default_storage.open('documents/' + filename + '_ru' + file_extension, 'r')

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


### Translate metadata: figure and tables captions and formula text in the format \caption{....} \text{...}
def meta_translate(metadata, target_language):
    recaption = regex.compile(r'(?<=\\caption\s*\{)((?:[^{}]++|\{(?1)\})*+)(?=\})|(?<=\\text\s*\{)((?:[^{}]++|\{(?2)\})*+)(?=\})')
    metadata_latex_tr = []

    for latex_string in metadata["latex"]:
        here = 0
        latex_string_tr=''

        for caption in recaption.finditer(latex_string):

            caption_text = caption.group()
            fmetadata={"comments": [], "latex": [], "commands": [], "notranslate": []}

            ### Replace LaTeX commands and formulas by tokens
            recommand = regex.compile(r'\s*\\title|\s*\\chapter\**|\s*\\section\**|\s*\\subsection\**|\s*\\subsubsection\**'
                    r'|\s*~*\\footnote[0-9]*|\s*(\$+)(?:(?!\1)[\s\S])*\1|\s*~*\\\%\s*'
                    r'|(\s*~*\\\w++\s*(\{(?:[^{}]++|(?3))*+\})?\s*(\{(?:[^{}]++|(?4))*+\})?)|\w*\\"\{\w\}\w*|\w*\\"\w++')
                    # comment: \3 and \4 because \1 is already used in front
            for m1 in recommand.finditer(caption_text):
                fmetadata["notranslate"].append(m1.group())
            def repl_f(obj):
                repl_f.nc += 1
                return '<span class="notranslate">[%d]</span>'%(repl_f.nc-1)
            repl_f.nc=0
            tokenized_caption_text=recommand.sub(repl_f,caption_text)

            ### Translate
            raw_caption_tr = main_app.basic.translate( tokenized_caption_text, target_language )

            ### Detokenize translation
            caption_tr, caption_JSONmessages = main_app.latex.detokenize( raw_caption_tr, fmetadata )

            latex_string_tr += latex_string[here:caption.start()] + caption_tr
            here=caption.end()

        latex_string_tr += latex_string[here:]
        metadata_latex_tr.append(latex_string_tr)

    metadata["latex"] = metadata_latex_tr
    return metadata


def translate(url, filename, target_language):
    ### Parse command line arguments: LaTeX source and target language
    # parser = argparse.ArgumentParser()
    # parser.add_argument('filename')
    # parser.add_argument('target_language')  # ISO 639-1 language code
    # args = parser.parse_args()


    if (regex.search('.tex$', url) == None):
        sys.exit('The input should be .tex file. Exit.')
    # filebase = regex.sub('.tex$', '', url)
    filebase = regex.sub('.tex$', '', filename)
    target_language = target_language
    print('LaTeX file:', url)
    print('Target language:', target_language)

    ### Load LaTeX source
    # with open(filename, 'r', encoding='utf-8') as source_file:
    #     source = source_file.read()

    # print('test' + args.filename)
    source = default_storage.open('documents/' + filename).read()
    # # content = default_storage.open('documents/' + '/documents/example.tex', 'r')
    # content = default_storage.url('/documents/' + '/example.tex')
    # response = HttpResponse(content, 'rb')
    # print(response)

    ### Tokenize LaTeX source
    tokenized_source, metadata = main_app.latex.tokenize(source.decode("utf-8"))

    ### Translate text
    # target_language must be an ISO 639-1 code: "ru", "en" etc.
    # See https://cloud.google.com/translate/docs/languages for the full list
    raw_translation = main_app.basic.translate(tokenized_source, target_language)

    metadata = meta_translate(metadata, target_language)

    ### Detokenize translation
    translation, JSONmessages = main_app.latex.detokenize(raw_translation, metadata)

    ### Save the result to .tex file
    output_filename = filebase + '_' + target_language + '.tex'
    # with open(output_filename, 'w', encoding='utf-8') as translation_file:
    #     translation_file.write(translation)

    default_storage.save('documents/' + filebase + '_' + target_language + '.tex', ContentFile(translation.encode('utf-8')))

    print('Output file:', output_filename)
    print(JSONmessages)
