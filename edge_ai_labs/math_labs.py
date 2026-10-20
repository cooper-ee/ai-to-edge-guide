"""Numerical reference implementations; these are not optimized GPU kernels."""
import numpy as np


def softmax(x, axis=-1):
    e = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return e / e.sum(axis=axis, keepdims=True)


def ml(seed=42):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(900, 4))
    y = (x @ np.array([2., -1.5, .7, .3]) + rng.normal(0, .4, 900) > 0).astype(float)
    # The split precedes ALL fitted preprocessing. Test data never select parameters.
    train, val, test = np.split(rng.permutation(len(x)), [540, 720])
    mean, std = x[train].mean(0), x[train].std(0).clip(1e-8)
    x = (x - mean) / std
    w, b = np.zeros(4), 0.
    def loss(ids):
        z = x[ids] @ w + b
        return float(np.mean(np.logaddexp(0, z) - y[ids] * z))
    initial = loss(train)
    best, best_state = float('inf'), None
    for _ in range(400):
        p = 1 / (1 + np.exp(-np.clip(x[train] @ w + b, -50, 50)))
        d = p - y[train]
        w -= .15 * x[train].T @ d / len(train)
        b -= .15 * d.mean()
        score = loss(val)
        if score < best:
            best, best_state = score, (w.copy(), float(b))
    w, b = best_state
    pred = (x[test] @ w + b > 0)
    tp = np.sum(pred & (y[test] == 1))
    fp = np.sum(pred & (y[test] == 0))
    fn = np.sum(~pred & (y[test] == 1))
    return dict(initial_train_loss=initial, final_train_loss=loss(train), val_loss=best,
                test_accuracy=float(np.mean(pred == y[test])),
                test_f1=float(2 * tp / max(2 * tp + fp + fn, 1)),
                split_sizes=[len(train), len(val), len(test)], seed=seed)


def gradients(seed=42):
    rng = np.random.default_rng(seed)
    x, w, y = rng.normal(size=(8, 3)), rng.normal(size=3), rng.normal(size=8)
    def f(a):
        return np.mean((x @ a - y) ** 2)
    analytic = 2 * x.T @ (x @ w - y) / len(y)
    eps = 1e-5
    numeric = np.zeros_like(w)
    for i in range(len(w)):
        delta = np.zeros_like(w)
        delta[i] = eps
        numeric[i] = (f(w + delta) - f(w - delta)) / (2 * eps)
    return dict(max_gradient_error=float(np.max(np.abs(analytic - numeric))), epsilon=eps)


def dense_attention(q, k, v, causal=False):
    scores = q @ k.T / np.sqrt(q.shape[-1])
    if causal:
        if len(q) != len(k):
            raise ValueError('Causal reference expects equal query/key length')
        scores = np.where(np.triu(np.ones(scores.shape, bool), 1), -np.inf, scores)
    return softmax(scores) @ v


def online_attention(q, k, v, block=5, causal=False):
    """Online softmax across key blocks; never creates the full N x N scores."""
    if block < 1 or (causal and len(q) != len(k)):
        raise ValueError('Invalid block or causal shape')
    outputs = []
    for i, query in enumerate(q):
        m, denom, accum = -np.inf, 0., np.zeros(v.shape[-1])
        end = i + 1 if causal else len(k)
        for start in range(0, end, block):
            s = k[start:min(start + block, end)] @ query / np.sqrt(q.shape[-1])
            new_m = max(m, float(s.max()))
            rescale = np.exp(m - new_m)
            p = np.exp(s - new_m)
            accum = accum * rescale + p @ v[start:min(start + block, end)]
            denom = denom * rescale + p.sum()
            m = new_m
        outputs.append(accum / denom)
    return np.stack(outputs)


def attention(seed=42):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(19, 16))
    q, k, v = [x @ rng.normal(size=(16, 8)) / 4 for _ in range(3)]
    full = dense_attention(q, k, v, causal=True)
    cached = np.stack([dense_attention(q[t:t + 1], k[:t + 1], v[:t + 1])[0]
                       for t in range(len(x))])
    blocked = online_attention(q, k, v, block=5, causal=True)
    return dict(cached_max_error=float(np.max(np.abs(full - cached))),
                blocked_max_error=float(np.max(np.abs(full - blocked))),
                shape=list(full.shape), block_size=5,
                note='Float64 numerical reference; not a GPU speed benchmark')


def kv_bytes(lengths, kv_heads, head_dims, batch=1, tokens=2048, element_bytes=2):
    """Layerwise full-attention payload only. Other recurrent states excluded."""
    if not (len(lengths) == len(kv_heads) == len(head_dims)):
        raise ValueError('Layer lists must align')
    values = [batch, tokens, element_bytes, *lengths, *kv_heads, *head_dims]
    if any(v < 0 for v in values):
        raise ValueError('Sizes must be nonnegative')
    return 2 * batch * tokens * element_bytes * sum(l * h * d for l, h, d in zip(lengths, kv_heads, head_dims))


def memory(seed=42):
    dense = kv_bytes([24], [4], [64])
    hybrid = kv_bytes([6], [4], [64])
    return dict(full_attention_KV_MiB=dense / 2**20,
                hybrid_full_attention_part_MiB=hybrid / 2**20,
                config=dict(layers=24, full_layers_in_hybrid=6, kv_heads=4,
                            head_dim=64, tokens=2048, batch=1, bytes_per_element=2),
                note='Synthetic configuration; recurrent state, weights and workspace excluded')


def quantize_dequantize(w, bits=8, per_channel=False, clip_percentile=100):
    if bits not in (4, 8) or not 0 < clip_percentile <= 100:
        raise ValueError('Expected 4/8 bits and percentile in (0, 100]')
    bound = 2**(bits - 1) - 1
    axis = 1 if per_channel else None  # row = output channel for W[out,in]
    a = np.percentile(np.abs(w), clip_percentile, axis=axis, keepdims=True)
    scale = np.maximum(a / bound, 1e-12)
    q = np.clip(np.rint(w / scale), -bound, bound).astype(np.int8)
    return q * scale, scale


def quantization(seed=42):
    rng = np.random.default_rng(seed)
    w = rng.normal(size=(32, 64)) * np.geomspace(.05, 4, 32)[:, None]
    w[0, 0] = 30  # a deliberately adverse outlier
    x = rng.normal(size=(100, 64))
    rows = []
    for bits, channel, percentile in [(8, False, 100), (8, True, 100),
                                     (4, True, 100), (4, True, 99)]:
        recon, scale = quantize_dequantize(w, bits, channel, percentile)
        rows.append(dict(bits=bits, per_channel=channel, percentile=percentile,
                         weight_mse=float(np.mean((w - recon)**2)),
                         output_mse=float(np.mean((x @ w.T - x @ recon.T)**2)),
                         ideal_weight_bytes=w.size * bits / 8,
                         scale_count=scale.size))
    return dict(comparisons=rows, note='INT4 values stored in int8 for clarity; no packed kernel or speed claim')


def compiler(seed=42):
    rng = np.random.default_rng(seed)
    a, b = rng.normal(size=(17, 11)), rng.normal(size=(11, 13))
    c = np.zeros((17, 13))
    for i in range(0, 17, 4):
        for j in range(0, 13, 4):
            for k in range(0, 11, 4):
                c[i:i+4, j:j+4] += a[i:i+4, k:k+4] @ b[k:k+4, j:j+4]
    # Illustrative sustained limits, NOT any real chip's specification.
    peak, bandwidth, intensity = 1e12, 20e9, 2.
    return dict(tiled_max_error=float(np.max(np.abs(c - a @ b))),
                illustrative_roofline_GFLOPs=min(peak, bandwidth * intensity) / 1e9,
                illustrative_knee_FLOPs_per_byte=peak / bandwidth,
                note='Python loop demonstrates tail tiles and algebra, not acceleration')
