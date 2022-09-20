from django.core.files.base import ContentFile
from django.shortcuts import render

from . import basic, latex
from .forms import DocumentForm

import urllib.request
from .models import DocumentTex

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.core.files.storage import default_storage

from django.http import HttpResponse
from django.http import JsonResponse

# trans
import argparse
import os

import regex
import sys
import pickle

import main_app.basic  # Interface to basic Google translation API
import main_app.latex  # LaTeX tokenizer

import urllib.parse

from core.views import base_view
import logging


logger = logging.getLogger(__name__)


class DocumentCreateView(CreateView):
    model = DocumentTex
    fields = ['filename', 'file', ]
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        documents = DocumentTex.objects.all()
        context['documents'] = documents
        return context


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@base_view
def post_model_form_upload(request):
    if is_ajax(request=request) and request.method == 'POST':
        if 'textarea1' in request.POST:

            language = urllib.parse.unquote(request.POST.get('language'))

            textarea1_for_translate = urllib.parse.unquote(request.POST.get('textarea1'))

            translation = translate_text(textarea1_for_translate, str(language))

            return JsonResponse({"translation": translation}, status=200)

    else:
        return JsonResponse({"error": 'error'}, status=400)


@base_view
def model_form_upload(request):
    error_text = ''
    if request.method == 'POST':
        if 'submit1' in request.POST:
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                doc = form.save()
                filename = request.FILES['file'].name
                doc.filename = filename
                doc.save()

                language_to = request.POST.get('language_to')

                # from django.http import HttpResponse
                # return HttpResponse(language_to)
                check_error = 0

                allowed = ['.tex']

                filename, file_extension = os.path.splitext(request.FILES['file'].name)
                if file_extension not in allowed:
                    check_error = 1
                    error_text = 'Please choose only .tex files'

                # if os.stat('documents/'+request.FILES['upload'].name).st_size > 1048576:
                #     check_error = 2

                if check_error != 0:
                    form = DocumentForm()
                    translation = ''

                else:
                    translate(default_storage.url(str(doc.file)), str(doc.file), language_to)

                    filename_hash, file_extension = os.path.splitext(str(doc.file))
                    content = default_storage.open(filename_hash + '_' + language_to + file_extension, 'r')

                    response = HttpResponse(content, 'rb')

                    default_storage.delete(filename_hash + file_extension)
                    default_storage.delete(filename_hash + '_' + language_to + file_extension)

                    response['Content-Type'] = 'text/plain'
                    response['Content-Disposition'] = 'attachment; filename="'+request.FILES['file'].name + '_' + language_to + file_extension+'"'
                    return response

        else:
            form = DocumentForm()
            translation = ''
    else:
        form = DocumentForm()
        translation = ''

    languages = {'': 'Select language'}
    languages['am'] = 'Amharic'
    languages['ar'] = 'Arabic'
    languages['eu'] = 'Basque'
    languages['bn'] = 'Bengali'
    languages['en-GB'] = 'English (UK)'
    languages['pt-BR'] = 'Portuguese (Brazil)'
    languages['bg'] = 'Bulgarian'
    languages['ca'] = 'Catalan'
    languages['chr'] = 'Cherokee'
    languages['hr'] = 'Croatian'
    languages['cs'] = 'Czech'
    languages['da'] = 'Danish'
    languages['nl'] = 'Dutch'
    languages['en'] = 'English (US)'
    languages['et'] = 'Estonian'
    languages['fil'] = 'Filipino'
    languages['fi'] = 'Finnish'
    languages['fr'] = 'French'
    languages['de'] = 'German'
    languages['el'] = 'Greek'
    languages['gu'] = 'Gujarati'
    languages['iw'] = 'Hebrew'
    languages['hi'] = 'Hindi'
    languages['hu'] = 'Hungarian'
    languages['is'] = 'Icelandic'
    languages['id'] = 'Indonesian'
    languages['it'] = 'Italian'
    languages['ja'] = 'Japanese'
    languages['kn'] = 'Kannada'
    languages['ko'] = 'Korean'
    languages['lv'] = 'Latvian'
    languages['lt'] = 'Lithuanian'
    languages['ms'] = 'Malay'
    languages['ml'] = 'Malayalam'
    languages['mr'] = 'Marathi'
    languages['no'] = 'Norwegian'
    languages['pl'] = 'Polish'
    languages['pt-PT'] = 'Portuguese (Portugal)'
    languages['ro'] = 'Romanian'
    languages['ru'] = 'Russian'
    languages['sr'] = 'Serbian'
    languages['zh-CN'] = 'Chinese (PRC)'
    languages['sk'] = 'Slovak'
    languages['sl'] = 'Slovenian'
    languages['es'] = 'Spanish'
    languages['sw'] = 'Swahili'
    languages['sv'] = 'Swedish'
    languages['ta'] = 'Tamil'
    languages['te'] = 'Telugu'
    languages['th'] = 'Thai'
    languages['zh-TW'] = 'Chinese (Taiwan)'
    languages['tr'] = 'Turkish'
    languages['ur'] = 'Urdu'
    languages['uk'] = 'Ukrainian'
    languages['vi'] = 'Vietnamese'
    languages['cy'] = 'Welsh'

    return render(request, 'main_app/index.html', {
        'form': form,
        'translation': translation,
        'languages': languages,
        'error_text': error_text,
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
    source = default_storage.open(filename).read()
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

    default_storage.save(filebase + '_' + target_language + '.tex', ContentFile(translation.encode('utf-8')))

    print('Output file:', output_filename)
    print(JSONmessages)


def translate_text(textarea1, target_language):

    # if (regex.search('.tex$', url) == None):
    #     sys.exit('The input should be .tex file. Exit.')
    # filebase = regex.sub('.tex$', '', filename)
    # target_language = target_language
    # print('LaTeX file:', url)
    # print('Target language:', target_language)

    # source = default_storage.open('documents/' + filename).read()
    source = textarea1

    ### Tokenize LaTeX source
    tokenized_source, metadata = main_app.latex.tokenize(source)

    ### Translate text
    raw_translation = main_app.basic.translate(tokenized_source, target_language)

    metadata = meta_translate(metadata, target_language)

    ### Detokenize translation
    translation, JSONmessages = main_app.latex.detokenize(raw_translation, metadata)

    ### Save the result to .tex file
    # output_filename = filebase + '_' + target_language + '.tex'
    #
    # default_storage.save('documents/' + filebase + '_' + target_language + '.tex', ContentFile(translation.encode('utf-8')))
    #
    # print('Output file:', output_filename)
    # print(JSONmessages)

    return translation
