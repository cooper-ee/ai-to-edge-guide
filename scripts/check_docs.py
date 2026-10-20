"""Offline check: local links/fragments, Python syntax, SVG XML and course count."""
import ast
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        for k in ['href','src']:
            if k in a:self.links.append(a[k])


def markdown_ids(s):
    ids=set()
    counts={}
    s=re.sub(r'```[\s\S]*?```','',s)
    for heading in re.findall(r'^#{1,6}\s+(.+)$',s,re.M):
        clean=re.sub(r'[^\w\s\-\u4e00-\u9fff]','',heading.lower()).strip().replace(' ','-')
        count=counts.get(clean,0)
        counts[clean]=count+1
        ids.add(clean+(f'-{count}' if count else ''))
    return ids


def check():
    errors=[];links=0;files=0
    for path in [*ROOT.rglob('*.md'),*ROOT.glob('*.html')]:
        if any(x in path.relative_to(ROOT).parts for x in ['artifacts','__pycache__','.venv']):continue
        files+=1;s=path.read_text(encoding='utf8')
        if path.suffix=='.md':
            clean=re.sub(r'```[\s\S]*?```','',s)
            targets=re.findall(r'!?\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)',clean)
            parser=Links();parser.feed(clean);targets+=parser.links
        else:
            parser=Links();parser.feed(s);targets=parser.links
        for link in targets:
            if urlsplit(link).scheme or link.startswith('//'):continue
            links+=1
            target,_,frag=unquote(link).partition('#')
            actual=(path.parent/target).resolve() if target else path
            if not actual.is_relative_to(ROOT):
                errors.append(f'{path.name}: link escapes repository: {link}');continue
            if not actual.exists():
                errors.append(f'{path.relative_to(ROOT)}: missing {link}');continue
            if frag and actual.is_file():
                txt=actual.read_text(encoding='utf8')
                if actual.suffix=='.md':ids=markdown_ids(txt)
                elif actual.suffix in ['.html','.svg']:
                    p=Links();p.feed(txt);ids=p.ids
                else:continue
                if frag not in ids:errors.append(f'{path.relative_to(ROOT)}: missing fragment {link}')
    python_files=[]
    for path in ROOT.rglob('*.py'):
        if any(x in path.relative_to(ROOT).parts for x in ['artifacts','.venv','__pycache__']):continue
        ast.parse(path.read_text(encoding='utf8'),filename=str(path));python_files.append(path)
    for path in (ROOT/'assets').glob('*.svg'):ET.parse(path)
    course_count=len(list((ROOT/'docs').glob('[0-9][0-9]-*.md')))
    if course_count!=18:errors.append(f'Expected 18 core courses, got {course_count}')
    result=dict(document_files=files,local_links_checked=links,python_files_parsed=len(python_files),
                courses=course_count,svg_files=len(list((ROOT/'assets').glob('*.svg'))),errors=errors)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)
    return result


if __name__=='__main__':check()
