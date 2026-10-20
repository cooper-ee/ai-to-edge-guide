"""Read-only GitHub Markdown preview check; this does not publish repository files.

Sends tutorial Markdown to GitHub's render endpoint and compares every math node
with the source. Network/API availability is separate from offline docs checks.
"""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import ssl
from urllib.request import Request,urlopen
try:
    from .markdown_math import parts
except ImportError:
    from markdown_math import parts

ROOT=Path(__file__).resolve().parents[1]


class MathNodes(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.math=[];self.current=None
    def handle_starttag(self,tag,attrs):
        if tag=='math-renderer':self.current=[]
    def handle_data(self,data):
        if self.current is not None:self.current.append(data)
    def handle_endtag(self,tag):
        if tag=='math-renderer' and self.current is not None:
            value=''.join(self.current).strip()
            delimiter='$$' if value.startswith('$$') else '$'
            assert value.endswith(delimiter)
            self.math.append(value[len(delimiter):-len(delimiter)].strip())
            self.current=None


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,default=ROOT/'artifacts/github-math')
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    docs=[];expected=[];counts=[]
    for path in sorted(ROOT.rglob('*.md')):
        if any(x in path.relative_to(ROOT).parts for x in ['artifacts','vendor','.venv','__pycache__']):continue
        source=path.read_text(encoding='utf8')
        formulae=[x.tex.strip() for x in parts(source) if x.kind in ('inline','display')]
        if not formulae:continue
        docs.append('# CHECK FILE: '+path.relative_to(ROOT).as_posix()+'\n\n'+source)
        expected.extend(formulae)
        counts.append(dict(path=path.relative_to(ROOT).as_posix(),formulae=len(formulae)))
    payload=json.dumps({'text':'\n\n---\n\n'.join(docs),'mode':'gfm'}).encode('utf8')
    req=Request('https://api.github.com/markdown',data=payload,method='POST',headers={
        'Content-Type':'application/json','Accept':'application/vnd.github+json',
        'User-Agent':'AI-to-Edge-Documentation-Check'})
    try:
        import certifi
        context=ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        context=ssl.create_default_context()
    with urlopen(req,context=context,timeout=60) as response:
        rendered=response.read().decode('utf8');status=response.status
    parser=MathNodes();parser.feed(rendered)
    compact=lambda x:re.sub(r'\s+','',x)
    matching=[compact(x) for x in expected]==[compact(x) for x in parser.math]
    report=dict(status=status,files=counts,source_formulae=len(expected),
                github_math_nodes=len(parser.math),formula_content_matches=matching,
                verification_scope='GitHub Markdown API parsing; local browser math typesetting checked separately',
                remote_repository_updated=False)
    (args.output/'github-math-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    (args.output/'github-fragment.html').write_text(rendered,encoding='utf8')
    bundle=(ROOT/'vendor/mathjax/tex-svg.js').as_uri()
    preview='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><style>body{max-width:1040px;margin:35px auto;background:#0d1117;color:#e6edf3;font:16px/1.9 "Microsoft YaHei",sans-serif;padding:24px}h1,h2{border-bottom:1px solid #30363d;padding-bottom:8px}a{color:#58a6ff}pre,code{background:#161b22;border-radius:5px;padding:4px}pre{padding:16px;overflow:auto}table{border-collapse:collapse}td,th{border:1px solid #30363d;padding:10px}img{max-width:100%}mjx-container[display=true]{overflow:auto}</style><script>window.MathJax={tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']]}};</script><script defer src="'''+bundle+'"></script><body>'+rendered+'</body></html>'
    (args.output/'github-preview.html').write_text(preview,encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))
    if not matching:raise SystemExit(1)


if __name__=='__main__':main()
