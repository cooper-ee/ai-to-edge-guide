"""Create a static batch=1 ONNX counterpart for a target compiler.
Host-side export tested locally; target compiler support must be checked separately.
"""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from edge_ai_labs.torch_labs import setup, load_classifier


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--artifacts',type=Path,default=Path('artifacts'))
    args = p.parse_args()
    torch = setup(42)
    model, mean, std = load_classifier(args.artifacts)
    class StaticPipeline(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.net = model
            self.register_buffer('mean',mean)
            self.register_buffer('std',std)
        def forward(self,x): return self.net((x-self.mean)/self.std)
    torch.onnx.export(StaticPipeline().eval(),(torch.zeros(1,4),),
                      str(args.artifacts/'classifier-static.onnx'),dynamo=True,
                      input_names=['features'],output_names=['logits'],
                      opset_version=18,external_data=False)
    print(args.artifacts/'classifier-static.onnx')


if __name__ == '__main__': main()
