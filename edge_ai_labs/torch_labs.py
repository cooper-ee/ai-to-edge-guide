"""Optional CPU PyTorch training, modern ONNX export, and a cached tiny LM."""
import json
from pathlib import Path
import numpy as np


def setup(seed):
    import torch
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    return torch


def model_class():
    import torch
    return torch.nn.Sequential(torch.nn.Linear(4, 16), torch.nn.ReLU(), torch.nn.Linear(16, 2))


def classifier(seed=42, output=Path('artifacts')):
    torch = setup(seed)
    rng = np.random.default_rng(seed)
    raw = rng.normal(size=(900, 4)).astype('float32')
    labels = (raw @ np.array([1.5, -2., .5, 1.]) + .25 * rng.normal(size=900) > 0).astype('int64')
    train, val, test = np.split(rng.permutation(900), [540, 720])
    mean, std = raw[train].mean(0), raw[train].std(0).clip(1e-8)
    x, y = torch.from_numpy((raw-mean)/std), torch.from_numpy(labels)
    model = model_class()
    opt = torch.optim.Adam(model.parameters(), lr=.02)
    criterion = torch.nn.CrossEntropyLoss()
    initial = float(criterion(model(x[train]), y[train]).item())
    best, state, curve = float('inf'), None, []
    for epoch in range(120):
        model.train()
        opt.zero_grad(set_to_none=True)
        loss = criterion(model(x[train]), y[train])
        loss.backward()
        opt.step()
        model.eval()
        with torch.inference_mode():
            v = float(criterion(model(x[val]), y[val]).item())
        if v < best:
            best = v
            state = {k:t.detach().clone() for k,t in model.state_dict().items()}
        curve.append(dict(epoch=epoch, train_loss=float(loss.item()), val_loss=v))
    model.load_state_dict(state)
    model.eval()
    with torch.inference_mode():
        acc = float((model(x[test]).argmax(-1) == y[test]).float().mean().item())
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    torch.save({'state_dict':state, 'mean':torch.from_numpy(mean), 'std':torch.from_numpy(std),
                'seed':seed, 'features':4}, output/'classifier.pt')
    np.savez(output/'classifier_cases.npz', x=raw[test], y=labels[test])
    (output/'training_curve.json').write_text(json.dumps(curve, indent=2), encoding='utf8')
    return dict(initial_train_loss=initial, selected_val_loss=best, test_accuracy=acc,
                parameters=sum(p.numel() for p in model.parameters()),
                epochs=120, seed=seed, checkpoint='classifier.pt',
                note='Synthetic data; an educational classifier, not a production accuracy claim')


def load_classifier(output):
    import torch
    ckpt = torch.load(Path(output)/'classifier.pt', map_location='cpu', weights_only=True)
    model = model_class().eval()
    model.load_state_dict(ckpt['state_dict'])
    return model, ckpt['mean'], ckpt['std']


def export(seed=42, output=Path('artifacts')):
    import onnx
    import onnxruntime as ort
    torch = setup(seed)
    output = Path(output)
    if not (output/'classifier.pt').exists():
        classifier(seed, output)
    model, mean, std = load_classifier(output)
    class Pipeline(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.net = model
            self.register_buffer('mean', mean)
            self.register_buffer('std', std)
        def forward(self, raw):
            return self.net((raw-self.mean)/self.std)
    pipeline = Pipeline().eval()
    example = torch.randn(4, 4)
    path = output/'classifier.onnx'
    batch = torch.export.Dim('batch', min=1, max=64)
    torch.onnx.export(pipeline, (example,), str(path), dynamo=True, opset_version=18,
                      input_names=['features'], output_names=['logits'],
                      dynamic_shapes=({0:batch},), external_data=False)
    onnx.checker.check_model(onnx.load(str(path)))
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(path), options, providers=['CPUExecutionProvider'])
    errors, agreements = [], []
    with torch.inference_mode():
        for n in [1, 7, 32, 64]:
            x = torch.randn(n, 4)
            ref = pipeline(x).numpy()
            actual = session.run(None, {'features':x.numpy()})[0]
            np.testing.assert_allclose(actual, ref, atol=1e-5, rtol=1e-4)
            errors.append(float(np.max(np.abs(actual-ref))))
            agreements.append(float(np.mean(actual.argmax(-1) == ref.argmax(-1))))
    # A trained-model evaluation, in addition to random numerical probes.
    data = np.load(output/'classifier_cases.npz')
    actual = np.concatenate([session.run(None, {'features':part})[0]
                             for part in np.array_split(data['x'], 3)])
    return dict(onnx_max_abs_error=max(errors), tested_batches=[1,7,32,64],
                argmax_agreement=min(agreements),
                onnx_test_accuracy=float(np.mean(actual.argmax(-1) == data['y'])),
                graph_checked=True, exporter='torch.export / dynamo=True', opset=18)


def tiny_lm(seed=42, output=Path('artifacts')):
    """One causal block with absolute positional embeddings and a real KV cache."""
    torch = setup(seed)
    nn, F = torch.nn, torch.nn.functional
    width, heads, context = 32, 4, 64
    # Original synthetic corpus; no downloads, copyrighted prose, or tokenizer dependency.
    corpus = ('red green blue . small models run on cpu . cache saves repeated work . '
              'check shapes before speed . learn test explain . ')*24
    vocab = sorted(set(corpus))
    stoi = {c:i for i,c in enumerate(vocab)}
    ids = torch.tensor([stoi[c] for c in corpus], dtype=torch.long)
    class TinyLM(nn.Module):
        def __init__(self):
            super().__init__()
            self.embed = nn.Embedding(len(vocab), width)
            self.pos = nn.Embedding(context, width)
            self.norm1, self.norm2 = nn.LayerNorm(width), nn.LayerNorm(width)
            self.qkv, self.proj = nn.Linear(width, 3*width), nn.Linear(width, width)
            self.ff = nn.Sequential(nn.Linear(width, 4*width), nn.GELU(), nn.Linear(4*width, width))
            self.head = nn.Linear(width, len(vocab))
        def forward(self, tokens, cache=None):
            b, t = tokens.shape
            offset = 0 if cache is None else cache[0].shape[-2]
            if offset + t > context:
                raise ValueError('Context capacity exceeded')
            x = self.embed(tokens) + self.pos(torch.arange(offset, offset+t))
            q, k, v = self.qkv(self.norm1(x)).chunk(3, -1)
            def split(a): return a.view(b,t,heads,width//heads).transpose(1,2)
            q, k, v = map(split, (q,k,v))
            if cache is not None:
                k, v = torch.cat([cache[0],k],-2), torch.cat([cache[1],v],-2)
            scores = q @ k.transpose(-1,-2) / (width//heads)**.5
            # Global query positions matter when a cached prefix exists.
            mask = torch.arange(k.shape[-2])[None,:] > torch.arange(offset,offset+t)[:,None]
            p = torch.softmax(scores.masked_fill(mask, -torch.inf), -1)
            a = (p @ v).transpose(1,2).contiguous().view(b,t,width)
            x = x + self.proj(a)
            x = x + self.ff(self.norm2(x))
            return self.head(x), (k,v)
    model = TinyLM()
    opt = torch.optim.AdamW(model.parameters(), lr=.004)
    curve = []
    for step in range(100):
        starts = torch.randint(0,len(ids)-25,(8,))
        x = torch.stack([ids[i:i+24] for i in starts])
        y = torch.stack([ids[i+1:i+25] for i in starts])
        opt.zero_grad(set_to_none=True)
        logits, _ = model(x)
        loss = F.cross_entropy(logits.reshape(-1,len(vocab)),y.reshape(-1))
        loss.backward()
        opt.step()
        curve.append(float(loss.item()))
    model.eval()
    probe = ids[:29][None,:]
    with torch.inference_mode():
        full, _ = model(probe)
        first, cache = model(probe[:,:11])
        pieces = [first]
        for i in range(11,probe.shape[1]):
            out, cache = model(probe[:,i:i+1],cache)
            pieces.append(out)
        cached = torch.cat(pieces,1)
        torch.testing.assert_close(cached, full, atol=1e-5, rtol=1e-4)
        future_changed = probe.clone()
        future_changed[:,20:] = (future_changed[:,20:]+1) % len(vocab)
        changed, _ = model(future_changed)
        causal_error = float((changed[:,:20]-full[:,:20]).abs().max().item())
        tokens, cache = ids[:10][None,:].clone(), None
        logits, cache = model(tokens)
        for _ in range(30):
            nxt = logits[:,-1,:].argmax(-1,keepdim=True)
            tokens = torch.cat([tokens,nxt],1)
            logits, cache = model(nxt,cache)
    output = Path(output)
    output.mkdir(parents=True,exist_ok=True)
    (output/'tiny_lm_curve.json').write_text(json.dumps(curve),encoding='utf8')
    torch.save({'state_dict':model.state_dict(),'vocab':vocab,'seed':seed,
                'width':width,'heads':heads,'context':context},output/'tiny_lm.pt')
    return dict(first_loss=curve[0], final_loss=curve[-1], steps=100,
                parameters=sum(p.numel() for p in model.parameters()),
                cached_logits_max_error=float((cached-full).abs().max().item()),
                future_leakage_max_error=causal_error,
                generated_example=''.join(vocab[i] for i in tokens[0].tolist()),
                note='Training-loss and numerical checks only; repeated toy corpus cannot establish generalization')
