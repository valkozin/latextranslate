#!/usr/bin/env python
#------------------------------------------------
# Machine translator for LaTeX documents
# Copyright (c) D. R. Gulevich & V. K. Kozin 2021
#------------------------------------------------
import argparse
import regex
import sys
import pickle
sys.path.append("..")
import latex # LaTeX tokenizer

INPUT_FROM_FILE=True
OUTPUT_TO_FILE=True

if(INPUT_FROM_FILE):
    ### Load raw translation
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    if(regex.search('_tr.token$',args.filename)==None):
        sys.exit('The input should be _tr.token file. Exit.')
    print('Tokenenized translation from:',args.filename)
    filebase = regex.sub('_tr.token$','',args.filename)
    with open(args.filename, 'r', encoding='utf-8') as source_file:
        raw_translation = source_file.read()

    ### Load metadata from binary files
    metadata={"comments": [], "latex": [], "commands": []}
    with open (filebase+'_comments.dat', 'rb') as fp:
        metadata["comments"] = pickle.load(fp)
    with open (filebase+'_commands.dat', 'rb') as fp:
        metadata["commands"] = pickle.load(fp)
    with open (filebase+'_latex.dat', 'rb') as fp:
        metadata["latex"] = pickle.load(fp)
    with open (filebase+'_notranslate.dat', 'rb') as fp:
        metadata["notranslate"] = pickle.load(fp)

### Detokenize translation
translation, JSONmessages = latex.detokenize( raw_translation, metadata )
print(JSONmessages)

### Save the processed output to .tex file
if(INPUT_FROM_FILE and OUTPUT_TO_FILE):
    output_filename = filebase + '_tr.tex'
    with open(output_filename, 'w', encoding='utf-8') as translation_file:
	    translation_file.write(translation)
    print('Output file:',output_filename)
