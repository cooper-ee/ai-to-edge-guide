"""Parse Markdown math without interpreting shell/code dollar signs as LaTeX.

Authoring conventions: $`...`$ inline and fenced ``math`` display blocks.
The legacy $...$ / $$...$$ forms can be migrated without changing code spans.
"""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Part:
    kind: str
    raw: str
    tex: str = ''


FENCE = re.compile(r'(?m)^ {0,3}(`{3,}|~{3,})([^\n]*)\n')


def _prose(source):
    parts=[]
    start=i=0
    while i<len(source):
        if source[i]=='$' and (i==0 or source[i-1]!='\\'):
            if source.startswith('$$',i):
                end=source.find('$$',i+2)
                kind,inner,close='display',i+2,2
            elif source.startswith('$`',i):
                end=source.find('`$',i+2)
                kind,inner,close='inline',i+2,2
            else:
                match=re.search(r'(?<![\\$])\$(?!\$)',source[i+1:])
                end=i+1+match.start() if match else -1
                kind,inner,close='inline',i+1,1
                if end!=-1 and '\n' in source[inner:end]:end=-1
            if end!=-1:
                if start<i:parts.append(Part('text',source[start:i]))
                parts.append(Part(kind,source[i:end+close],source[inner:end]))
                i=end+close;start=i;continue
        if source[i]=='`':
            count=len(re.match(r'`+',source[i:]).group())
            marker='`'*count
            end=source.find(marker,i+count)
            if end!=-1:
                if start<i:parts.append(Part('text',source[start:i]))
                parts.append(Part('code',source[i:end+count]))
                i=end+count;start=i;continue
        i+=1
    if start<len(source):parts.append(Part('text',source[start:]))
    return parts


def parts(source):
    """Yield text/code/inline/display parts, preserving non-math bytes."""
    result=[];cursor=0
    while True:
        opening=FENCE.search(source,cursor)
        if not opening:
            result.extend(_prose(source[cursor:]));break
        result.extend(_prose(source[cursor:opening.start()]))
        marker=opening.group(1)
        closing=re.compile(r'(?m)^ {0,3}'+re.escape(marker[0])+'{'+str(len(marker))+r',}[ \t]*(?:\n|$)').search(source,opening.end())
        end=closing.end() if closing else len(source)
        raw=source[opening.start():end]
        if opening.group(2).strip()=='math':
            if not closing:raise ValueError('Unclosed fenced math block')
            result.append(Part('display',raw,source[opening.end():closing.start()].strip()))
        else:
            result.append(Part('code',raw))
        cursor=end
    return result


def compatible_tex(tex):
    tex=re.sub(r'\\operatorname\{([^{}]+)\}',r'\\mathrm{\1}',tex)
    tex=re.sub(r'\\frac([12])n',r'\\frac{\1}{n}',tex)
    tex=tex.replace('<',r'\lt ').replace('>',r'\gt ')
    return tex.strip()


def normalize(source):
    output=[]
    for part in parts(source):
        if part.kind=='inline':output.append('$`'+compatible_tex(part.tex)+'`$')
        elif part.kind=='display':
            # Keep a separating blank line even for two adjacent display blocks.
            output.append('\n\n```math\n'+compatible_tex(part.tex)+'\n```\n\n')
        else:output.append(part.raw)
    # Trim blank runs only outside protected code blocks.
    normalized=''.join(output)
    return ''.join(re.sub(r'\n{3,}','\n\n',p.raw) if p.kind=='text' else p.raw
                   for p in parts(normalized))


def for_html(source):
    """Return Markdown-safe placeholders and HTML/MathJax replacements."""
    import html
    output=[];replacements=[]
    for part in parts(source):
        if part.kind not in ('inline','display'):
            output.append(part.raw);continue
        token=f'ZZEDGEMATH{len(replacements):04d}ZZ'
        tex=html.escape(compatible_tex(part.tex))
        if part.kind=='inline':replacement='<span class="math-inline">\\('+tex+'\\)</span>'
        else:replacement='<div class="math-display">\\['+tex+'\\]</div>'
        output.append(token)
        replacements.append((token,replacement,part.kind))
    return ''.join(output),replacements


def audit(source):
    errors=[];inline=display=0
    for part in parts(source):
        if part.kind in ('inline','display'):
            if part.kind=='inline':
                inline+=1
                if not part.raw.startswith('$`'):errors.append('Use protected inline math delimiters')
            else:
                display+=1
                if not part.raw.lstrip().startswith('```math'):errors.append('Use a fenced math display block')
            if re.search(r'\\operatorname\b',part.tex):errors.append('Replace operatorname with a supported basic macro')
            if '<' in part.tex or '>' in part.tex:errors.append('Use TeX lt/gt for HTML-sensitive comparisons')
            # Catch an unbalanced group before handing it to a math renderer.
            depth=0
            for char in re.sub(r'\\[{}]','',part.tex):
                if char=='{':depth+=1
                elif char=='}':depth-=1
                if depth<0:break
            if depth!=0:errors.append('Unbalanced braces in formula')
        elif part.kind=='text' and re.search(r'(?<!\\)\$',part.raw):
            errors.append('Unpaired/unprotected dollar sign outside code')
    return dict(inline=inline,display=display,errors=errors)
