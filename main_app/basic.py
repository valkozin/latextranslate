#!/usr/bin/env python
#------------------------------------------------
# Machine translator for LaTeX documents
# Copyright (c) D. R. Gulevich & V. K. Kozin 2021
#------------------------------------------------
# basic.py : interface to Google translation basic API
#------------------------------------------------
import os
import six
from google.cloud import translate_v2
import regex

# Set the environment variables
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './textranslate-97a001f8c19c.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.dirname(os.path.abspath(__file__)) + '/textranslate-97a001f8c19c.json'

# Target must be an ISO 639-1 language code.
# https://cloud.google.com/translate/docs/languages
def translate_chunk( text, target ):
    translate_client = translate_v2.Client()
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")
    result = translate_client.translate(text, target_language=target, format_='html') # Text can also be a sequence of strings
    return result

### Split into chunks, translate and joint
# 5000 characters recommended request length, see https://cloud.google.com/translate/quotas
def translate( original_text, target, CHARLIMIT=5000 ):
    start=0
    end=0
    translated_chunks=[]
    for m in regex.finditer(r'\.<br>',original_text):
        if(m.end()-start<CHARLIMIT):
            end=m.end()
        else:
            if(end>start):
                chunk_result = translate_chunk(original_text[start:end], target)
                translated_chunks.append(chunk_result["translatedText"])
            start=end
            end=m.end()
    chunk_result = translate_chunk( original_text[start:], target )
    translated_chunks.append( chunk_result["translatedText"] )
    translated_text = ''.join(translated_chunks) # Join chunks
    
    return translated_text
