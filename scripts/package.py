"""Package reviewable tutorial files, excluding local models and caches."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile
from check_docs import check

ROOT=Path(__file__).resolve().parents[1]
EXCLUDE={'artifacts','__pycache__','.venv','.git','.pytest_cache'}


def files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file()
                  and not any(x in EXCLUDE for x in p.relative_to(ROOT).parts)
                  and p.suffix not in {'.pt','.onnx','.gguf','.rknn','.rkllm','.pyc'})


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--name',default='ai-to-edge-guide')
    parser.add_argument('--version',default='1.1')
    args=parser.parse_args()
    if not args.name or any(x in args.name for x in '/\\:'):
        parser.error('Archive name must be a simple folder name')
    report=check()
    (ROOT/'reports/docs-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    manifest=[]
    for p in files():
        if p==ROOT/'reports/file-manifest.json':continue
        data=p.read_bytes()
        manifest.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    (ROOT/'reports/file-manifest.json').write_text(json.dumps({'version':args.version+'.0','files':manifest},ensure_ascii=False,indent=2),encoding='utf8')
    archive=ROOT.parent/(args.name+'-v'+args.version+'.zip')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files():z.write(p,args.name+'/'+p.relative_to(ROOT).as_posix())
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.SHA256.txt').write_text(digest+'  '+archive.name+'\n',encoding='ascii')
    print(json.dumps(dict(archive=str(archive),files=len(files()),bytes=archive.stat().st_size,sha256=digest),indent=2))


if __name__=='__main__':main()
