import argparse
import importlib.metadata
import json
from pathlib import Path
import platform
import time
from . import math_labs, systems

CORE = {'ml':math_labs.ml, 'gradients':math_labs.gradients,
        'attention':math_labs.attention, 'memory':math_labs.memory,
        'quantization':math_labs.quantization, 'serving':systems.serving,
        'rag':systems.rag, 'compiler':math_labs.compiler}


def run(lab, seed, output):
    if lab in CORE:
        return CORE[lab](seed)
    from . import torch_labs
    return {'classifier':torch_labs.classifier,'export':torch_labs.export,
            'tiny-lm':torch_labs.tiny_lm}[lab](seed, output)


def main():
    parser = argparse.ArgumentParser(description='AI to edge: inspectable CPU experiments')
    parser.add_argument('--lab', choices=[*CORE,'classifier','export','tiny-lm','all','full'], default='all')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--output', type=Path, default=Path('artifacts'))
    args = parser.parse_args()
    labs = list(CORE) if args.lab == 'all' else [*CORE,'classifier','export','tiny-lm'] if args.lab == 'full' else [args.lab]
    versions = {}
    for name in ['numpy','torch','onnx','onnxruntime','onnxscript','onnx_ir']:
        try: versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: pass
    report = dict(seed=args.seed, python=platform.python_version(), platform=platform.platform(),
                  dependencies=versions, experiments={})
    args.output.mkdir(parents=True,exist_ok=True)
    for name in labs:
        start = time.perf_counter()
        result = run(name,args.seed,args.output)
        report['experiments'][name] = {'elapsed_s':time.perf_counter()-start,'metrics':result}
        print(f'[OK] {name}: {json.dumps(result,ensure_ascii=False)}')
    dest = args.output / f'report-{args.lab}.json'
    dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(f'Report: {dest.resolve()}')


if __name__ == '__main__':
    main()
