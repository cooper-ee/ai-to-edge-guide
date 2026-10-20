"""Hardware-dependent adapter template; not executed in this delivery.
Run in an isolated, official RKNN-Toolkit2-supported host environment.
Check that your SDK accepts the ONNX opset/operators before conversion.
"""
import argparse
import hashlib
import json
from pathlib import Path


def check(code,stage):
    if code != 0:
        raise RuntimeError(f'{stage} failed with code {code}')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--model',type=Path,required=True)
    p.add_argument('--target',default='rk3576')
    p.add_argument('--dataset',type=Path,help='SDK-format calibration list; no dataset means floating baseline')
    p.add_argument('--output',type=Path,default=Path('artifacts/model.rknn'))
    args = p.parse_args()
    if not args.model.is_file(): p.error('ONNX model does not exist')
    if args.dataset is not None and not args.dataset.is_file(): p.error('Dataset list does not exist')
    from rknn.api import RKNN
    args.output.parent.mkdir(parents=True,exist_ok=True)
    rknn = RKNN(verbose=True)
    try:
        check(rknn.config(target_platform=args.target),'config')
        check(rknn.load_onnx(model=str(args.model)),'load_onnx')
        check(rknn.build(do_quantization=args.dataset is not None,
                         dataset=None if args.dataset is None else str(args.dataset)),'build')
        check(rknn.export_rknn(str(args.output)),'export_rknn')
    finally:
        rknn.release()
    manifest = dict(input_sha256=hashlib.sha256(args.model.read_bytes()).hexdigest(),
                    artifact_sha256=hashlib.sha256(args.output.read_bytes()).hexdigest(),
                    target=args.target,quantized=args.dataset is not None,
                    status='converted only; board execution and correctness NOT validated')
    args.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')


if __name__ == '__main__': main()
