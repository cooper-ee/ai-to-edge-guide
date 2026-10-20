"""CPU inference microbenchmark. Execute from the repository root."""
import argparse
import json
from pathlib import Path
import platform
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from edge_ai_labs.torch_labs import setup, load_classifier


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--artifacts',type=Path,default=Path('artifacts'))
    p.add_argument('--repeats',type=int,default=300)
    args = p.parse_args()
    if args.repeats < 30: p.error('At least 30 samples required')
    torch = setup(42)
    model, mean, std = load_classifier(args.artifacts)
    rows = []
    with torch.inference_mode():
        for batch in [1,8,32,64]:
            # Inputs are preallocated. Tensor creation and HTTP overhead excluded.
            x = torch.randn(batch,4)
            def infer(): return model((x-mean)/std)
            for _ in range(30): infer()
            times = []
            for _ in range(args.repeats):
                start = time.perf_counter_ns()
                infer()
                times.append((time.perf_counter_ns()-start)/1e6)
            rows.append(dict(batch=batch, p50_ms=float(np.percentile(times,50)),
                             p95_ms=float(np.percentile(times,95)),
                             samples_per_s=batch/(float(np.mean(times))/1000),
                             raw_latency_ms=times))
    report = dict(device='cpu',threads=1,warmup=30,repeats=args.repeats,seed=42,
                  python=platform.python_version(),torch=torch.__version__,
                  scope='in-process preprocessing + forward; excludes allocation, queue, HTTP and serialization',
                  measurements=rows)
    dest = args.artifacts/'benchmark.json'
    dest.write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps({**report,'measurements':[{k:v for k,v in r.items() if k!='raw_latency_ms'} for r in rows]},indent=2))


if __name__ == '__main__': main()
