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
    ### Parse input LaTeX
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    if(regex.search('.tex$',args.filename)==None):
        sys.exit('The input should be .tex file. Exit.')
    print('LaTeX file:',args.filename)
    filebase = regex.sub('.tex$','',args.filename)
    with open(args.filename, 'r',  encoding='utf-8') as source_file:
        source = source_file.read()

### Process LaTeX
text, metadata = latex.tokenize(source)

if(OUTPUT_TO_FILE):
    ### Save processed text to .tok file
    output_filename = filebase + '.token'
    with open(output_filename, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)
    print('Processed text saved to:',output_filename)

    ### Save metadata to binary files
    with open(filebase+'_comments.dat', 'wb') as fp:
        pickle.dump(metadata["comments"], fp)
    with open(filebase+'_latex.dat', 'wb') as fp:
        pickle.dump(metadata["latex"], fp)
    with open(filebase+'_commands.dat', 'wb') as fp:
        pickle.dump(metadata["commands"], fp)
    with open(filebase+'_notranslate.dat', 'wb') as fp:
        pickle.dump(metadata["notranslate"], fp)
