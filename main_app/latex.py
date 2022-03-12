#!/usr/bin/env python
#------------------------------------------------
# Machine translator for LaTeX documents
# Copyright (c) D. R. Gulevich & V. K. Kozin 2021
#------------------------------------------------
# LaTeX tokenizer
#------------------------------------------------
import regex
import json

def tokenize(source):

    metadata={"comments": [], "latex": [], "commands": [], "notranslate": []}

    ### Hide all comments : a sequence of lines starting with % (but not \%), possibly separated by \s*
    recomment = regex.compile(r'(?<!\\)((?:[%].*(?:\n|$)\s*)++)')

    for m in recomment.finditer(source):
        metadata["comments"].append(m.group())
    def repl_comment(obj):
        repl_comment.ncomment += 1
        return '_LTR_COMMENT_%d_'%(repl_comment.ncomment-1)
    repl_comment.ncomment=0
    text=recomment.sub(repl_comment,source)
    
    ### Hide everything that is beyond \begin{document} ... \end{document}
    bdoc=regex.search(r'\\begin\{document\}',text)
    edoc=regex.search(r'\\end\{document\}',text)
    if(bdoc!=None):
        preamble=text[:bdoc.end()]
        metadata["latex"].append(preamble)
        if(edoc!=None):
#            maintext = '<span class="notranslate">[1.0]</span>' + text[bdoc.end():edoc.start()]
            maintext = '_LTR_LATEX_0_' + text[bdoc.end():edoc.start()]
            postamble=text[edoc.start():]
        else:
#            maintext = '<span class="notranslate">[1.0]</span>' + text[bdoc.end():]
            maintext = '_LTR_LATEX_0_' + text[bdoc.end():]
            postamble=[]
    else:
        maintext=text
        postamble=[]
    text=maintext
    
    ### Hide LaTeX constructs \begin{...} ... \end{...}
    start_values=[]
    end_values=[]
    for m in regex.finditer(r'\\begin{ *equation\** *}|\\begin{ *figure\** *}|\\begin{ *eqnarray\** *}|\\begin{ *multline\** *}'
        r'|\\begin{ *thebibliography *}|\\begin{ *verbatim\** *}|\\begin{ *table\** *}|\\begin{ *subequations\** *}|\\begin{ *align\** *}'
        r'|\\begin{ *displaymath\** *}|\\begin{ *gather\** *}|\\\[',text):
        start_values.append(m.start())
    for m in regex.finditer(r'\\end{ *equation\** *}|\\end{ *figure\** *}|\\end{ *eqnarray\** *}|\\end{ *multline\** *}'
        r'|\\end{ *thebibliography *}|\\end{ *verbatim\** *}|\\end{ *table\** *}|\\end{ *subequations\** *}|\\end{ *align\** *}'
        r'|\\end{ *displaymath\** *}|\\end{ *gather\** *}|\\\]',text):
        end_values.append(m.end())
    nitems=len(start_values)
    assert(len(end_values)==nitems)
    if(nitems>0):
        newtext=text[:start_values[0]]
        for neq in range(nitems-1):
            metadata["latex"].append(text[start_values[neq]:end_values[neq]])
#            newtext += '<span class="notranslate">[1.%d]</span>'%(len(metadata["latex"])-1) + text[end_values[neq]:start_values[neq+1]]
            newtext += '_LTR_LATEX_%d_'%(len(metadata["latex"])-1) + text[end_values[neq]:start_values[neq+1]]
        metadata["latex"].append(text[start_values[nitems-1]:end_values[nitems-1]])
#        newtext += '<span class="notranslate">[1.%d]</span>'%(len(metadata["latex"])-1) + text[end_values[nitems-1]:]
        newtext += '_LTR_LATEX_%d_'%(len(metadata["latex"])-1) + text[end_values[nitems-1]:]
        text=newtext
    
    if(postamble!=[]):
        metadata["latex"].append(postamble)
#        text += '<span class="notranslate">[1.%d]</span>'%(len(metadata["latex"])-1)
        text += '_LTR_LATEX_%d_'%(len(metadata["latex"])-1)

    ### Replace LaTeX commands and formulas by tokens
    recommand = regex.compile(r'\s*\\title|\s*\\chapter\**|\s*\\section\**|\s*\\subsection\**|\s*\\subsubsection\**|\s*~*\\footnote[0-9]*|\s*(\$+)(?:(?!\1)[\s\S])*\1|\s*~*\\\%\s*|(\s*~*\\\w++\s*(\{(?:[^{}]++|(?3))*+\})?\s*(\{(?:[^{}]++|(?4))*+\})?)|\w*\\"\{\w\}\w*|\w*\\"\w++')
    # \3 and \4 because \1 already used in front

    for m in recommand.finditer(text):
        metadata["commands"].append(m.group())
    def repl_f(obj):
        repl_f.nc += 1
#        return '<span class="notranslate">[2.%d]</span>'%(repl_f.nc-1)
        return '_LTR_COMMAND_%d_'%(repl_f.nc-1)
    repl_f.nc=0
    text=recommand.sub(repl_f,text)

    ### Wrap tokens by HTML notranslate
    retok = regex.compile(r'(\s*_LTR_COMMENT_[0-9]++_|\s*_LTR_LATEX_[0-9]++_|\s*_LTR_COMMAND_[0-9]++_)++\s*')
    for m in retok.finditer(text):
        metadata["notranslate"].append(m.group())
    def rep(obj):
        rep.n += 1
        return '<span class="notranslate">[%d]</span>'%(rep.n-1)
    rep.n=0
    text=retok.sub(rep,text)

    ### New line character fix
    text=regex.sub('\n','<br>',text)

    return text,metadata


def detokenize(trtext, metadata):

    ### Replace weird characters introduced by translation
    trtext=regex.sub('\u200B',' ',trtext)

    ### Fix spacing
    trtext = regex.sub(r'\\ ',r'\\',trtext)
    trtext = regex.sub(' ~ ','~',trtext)
    trtext = regex.sub(' {','{',trtext)

    ### Restore new line character
    trtext=regex.sub('<br> ?','\n',trtext)

    ### Restore tokens
    here=0
    newtext=''
    nl=0
    messages = { 
        'Warning': {'Repeated': []},
        'Error': {'Corrupted': []}
    }
    for m in regex.finditer(' ?<span class="notranslate">\[[0-9]++\]</span> ?',trtext):
        n=int( regex.search('[0-9]++',m.group()).group() )
        if(n==nl):
            newtext += trtext[here:m.start()] + metadata["notranslate"][n]
            nl+=1
        elif(n==nl-1):
            messages['Warning']['Repeated'].append(metadata["latex"][n])
            newtext += trtext[here:m.start()] + metadata["latex"][n]
        else:
            messages['Error']['Corrupted'].append('[%d]'%nl)
            nl+=1
        here=m.end()
    newtext += trtext[here:]
    trtext=newtext

    ### Restore commands
    #ncomment=0 # used for code testing
    here=0
    newtext=''
    for m in regex.finditer('_LTR_COMMAND_[0-9]++_',trtext):
        n=int( regex.search('[0-9]++',m.group()).group() )
        newtext += trtext[here:m.start()] + metadata["commands"][n]
        here=m.end()
    newtext += trtext[here:]
    trtext=newtext

    ### Restore latex
    #ncomment=0 # used for code testing
    here=0
    newtext=''
    for m in regex.finditer('_LTR_LATEX_[0-9]++_',trtext):
        n=int( regex.search('[0-9]++',m.group()).group() )
        newtext += trtext[here:m.start()] + metadata["latex"][n]
        here=m.end()
    newtext += trtext[here:]
    trtext=newtext

    ### Restore comments
    #ncomment=0 # used for code testing
    here=0
    newtext=''
    for m in regex.finditer('_LTR_COMMENT_[0-9]++_',trtext):
        n=int( regex.search('[0-9]++',m.group()).group() )
    ### The lines below can be used to verify that all comments are restored
    #    if(n!=ncomment):
    #        print('Comment token ',m.group(),'is broken. Stopping.')
    #        break
    #    ncomment+=1
        newtext += trtext[here:m.start()] + metadata["comments"][n]
        here=m.end()
    newtext += trtext[here:]
    trtext=newtext

    return trtext, json.dumps(messages)
