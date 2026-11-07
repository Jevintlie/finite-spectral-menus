"""Build the included TeX sources without shell escape or network dependencies."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent
for program,args in [('pdflatex',['-no-shell-escape','-interaction=nonstopmode','-halt-on-error','main.tex']),
                     ('bibtex',['main']),
                     ('pdflatex',['-no-shell-escape','-interaction=nonstopmode','-halt-on-error','main.tex']),
                     ('pdflatex',['-no-shell-escape','-interaction=nonstopmode','-halt-on-error','main.tex'])]:
    result=subprocess.run([program,*args],cwd=ROOT,capture_output=True,text=True)
    if result.returncode:
        print(result.stdout[-10000:])
        print(result.stderr)
        raise SystemExit(result.returncode)
print('Built',ROOT/'main.pdf')
