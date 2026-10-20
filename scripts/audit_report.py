"""Check educational experiment acceptance criteria; optionally verify static ONNX."""
import argparse
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--report',type=Path,default=Path('artifacts/report-full.json'))
    p.add_argument('--output',type=Path,default=Path('artifacts/audit.json'))
    args=p.parse_args()
    r=json.loads(args.report.read_text(encoding='utf8'))['experiments']
    m=lambda name:r[name]['metrics']
    checks={
        'ml_loss_decreased':m('ml')['final_train_loss']<m('ml')['initial_train_loss'],
        'ml_heldout_accuracy_above_85_percent':m('ml')['test_accuracy']>.85,
        'gradient_finite_difference':m('gradients')['max_gradient_error']<1e-8,
        'numpy_cached_attention':m('attention')['cached_max_error']<1e-11,
        'numpy_blocked_attention':m('attention')['blocked_max_error']<1e-11,
        'memory_MiB_units':m('memory')['full_attention_KV_MiB']==48,
        'retrieval_toy_questions':m('rag')['recall_at_2']==1,
        'unknown_tool_rejected':m('rag')['unknown_tool_rejected'],
        'tiled_matmul_tail':m('compiler')['tiled_max_error']<1e-10,
        'classifier_heldout_accuracy_above_85_percent':m('classifier')['test_accuracy']>.85,
        'onnx_logits_error':m('export')['onnx_max_abs_error']<1e-4,
        'onnx_tested_batch_sizes':m('export')['tested_batches']==[1,7,32,64],
        'tiny_lm_training_loss_decreased':m('tiny-lm')['final_loss']<m('tiny-lm')['first_loss'],
        'tiny_lm_cached_logits':m('tiny-lm')['cached_logits_max_error']<1e-4,
        'tiny_lm_no_future_leakage':m('tiny-lm')['future_leakage_max_error']<1e-7,
    }
    extra={}
    static=args.report.parent/'classifier-static.onnx'
    if static.exists():
        import onnx
        import onnxruntime as ort
        import numpy as np
        import sys
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
        from edge_ai_labs.torch_labs import setup,load_classifier
        torch=setup(2026)
        model,mean,std=load_classifier(args.report.parent)
        onnx.checker.check_model(onnx.load(str(static)))
        session=ort.InferenceSession(str(static),providers=['CPUExecutionProvider'])
        worst=0.
        with torch.inference_mode():
            for _ in range(10):
                x=torch.randn(1,4)*3
                expected=model((x-mean)/std).numpy()
                actual=session.run(None,{'features':x.numpy()})[0]
                np.testing.assert_allclose(actual,expected,atol=1e-5,rtol=1e-4)
                worst=max(worst,float(np.max(np.abs(actual-expected))))
        checks['static_onnx_checker_and_numerical_probes']=True
        extra['static_onnx_max_abs_error']=worst
    result=dict(passed=all(checks.values()),checks=checks,**extra,
                scope='Local educational experiments; no GPU/NPU/third-party-runtime performance certification')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result,indent=2))
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
