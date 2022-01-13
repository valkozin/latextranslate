#!/usr/bin/env python
#------------------------------------------------
# Machine translator for LaTeX documents
# Copyright (c) D. R. Gulevich & V. K. Kozin 2021
#------------------------------------------------
import argparse
import regex
import sys
import pickle
import basic  # Interface to basic Google translation API
import latex  # LaTeX tokenizer

### Parse command line arguments: LaTeX source and target language
parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('target_language') # ISO 639-1 language code
args = parser.parse_args()
if(regex.search('.tex$',args.filename)==None):
    sys.exit('The input should be .tex file. Exit.')
filebase = regex.sub('.tex$','',args.filename)
target_language = args.target_language 
print('LaTeX file:',args.filename)
print('Target language:',target_language)

### Load LaTeX source
with open(args.filename, 'r',  encoding='utf-8') as source_file:
    source = source_file.read()

### Tokenize LaTeX source
tokenized_source, metadata = latex.tokenize( source )

### Translate text
# target_language must be an ISO 639-1 code: "ru", "en" etc.
# See https://cloud.google.com/translate/docs/languages for the full list
raw_translation = basic.translate( tokenized_source, target_language )

### Translate metadata: figure and tables captions and formula text in the format \caption{....} \text{...}
def meta_translate(metadata):    
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
            raw_caption_tr = basic.translate( tokenized_caption_text, target_language )

            ### Detokenize translation
            caption_tr, caption_JSONmessages = latex.detokenize( raw_caption_tr, fmetadata )

            latex_string_tr += latex_string[here:caption.start()] + caption_tr
            here=caption.end()

        latex_string_tr += latex_string[here:]
        metadata_latex_tr.append(latex_string_tr)

    metadata["latex"] = metadata_latex_tr
    return metadata

metadata = meta_translate(metadata)

### Detokenize translation
translation, JSONmessages = latex.detokenize( raw_translation, metadata )

### Save the result to .tex file
output_filename = filebase + '_' + target_language + '.tex'
with open(output_filename, 'w', encoding='utf-8') as translation_file:
	translation_file.write(translation)
print('Output file:',output_filename)
print(JSONmessages)
