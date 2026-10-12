# LaTeX source

This source builds the combined article and reduced public supplementary appendix for **Auditing Agent-Memory Benchmarks: Question-Blind Cues, Fair Nulls, and Replica Controls**, by Özgür Uğurlu.

Use a current TeX Live or MacTeX installation with pdfLaTeX and BibTeX. From this directory:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The result is `main.pdf`. Alternatively, run `pdflatex main.tex`, `bibtex main`, then `pdflatex main.tex` twice. The bibliography is author-year, using `natbib` and the standard `plainnat` style. The six figures are vector PDFs. The source uses the standard `article` class and standard TeX packages; it requires no conference style or external data.

The separate Markdown paper and appendix provide the GitHub reading version. The supplementary appendix explicitly describes its reduced public scope.
