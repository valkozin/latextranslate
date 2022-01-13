# latextranslator

LaTeX commands are replaced by tokens wrapped into ``<span class="notranslate">...</span>``.

## Usage

$ ./main.py <input_file> <target_language>

e.g.

$ ./main.py tests/test.tex ru

## Implementation

The translation is implemented in 3 stages:

*Stage 1*: call to ``latex.tokenize()``

*Stage 2*: call to ``basic.translate()``

*Stage 3*: call to ``latex.detokenize()``

## Unit tests

Independent unit tests for the methods ``tokenize()``, ``translate()`` and ``detokenize()`` are available in the ``tests\`` folder.


