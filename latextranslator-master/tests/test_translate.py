#!/usr/bin/env python
#------------------------------------------------
# Machine translator for LaTeX documents
# Copyright (c) D. R. Gulevich & V. K. Kozin 2021
#------------------------------------------------
import argparse
import regex
import sys
import os
sys.path.append("..")
import basic # Interface to basic Google translation API

### Reload the credentials path
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../textranslate-97a001f8c19c.json'

INPUT_FROM_FILE=True
OUTPUT_TO_FILE=True

### Load protected LaTeX source from file
if(INPUT_FROM_FILE):
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    if(regex.search('.token$',args.filename)==None):
        sys.exit('The input should be .token file. Exit.')
    print('Input file:',args.filename)
    filebase = regex.sub('.token$','',args.filename)
    with open(args.filename, 'r', encoding='utf-8') as source_file:
        tokenized_source = source_file.read()

### Translate text
raw_translation = basic.translate( tokenized_source, "ru" )

if(INPUT_FROM_FILE and OUTPUT_TO_FILE):
    ### Output translation to file
    output_filename = filebase + '_tr.token'
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        output_file.write(raw_translation)
    print('Tokenized translation:',output_filename)
