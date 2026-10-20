"""Deterministic serving simulation and local retrieval/tool demonstration."""
import math
import re
from collections import Counter
import numpy as np


def simulate(lengths, slots=2, continuous=True):
    """All arrive at tick 0. One active sequence emits one token per tick."""
    if slots < 1 or any(n < 1 for n in lengths):
        raise ValueError('Positive slots and output lengths required')
    pending, active, completed, trace, tick = list(enumerate(lengths)), [], {}, [], 0
    while pending or active:
        if continuous or not active:
            while pending and len(active) < slots:
                idx, length = pending.pop(0)
                active.append([idx, length])
        trace.append([r[0] for r in active])
        tick += 1
        for r in active:
            r[1] -= 1
            if r[1] == 0:
                completed[r[0]] = tick
        active = [r for r in active if r[1] > 0]
    return dict(makespan_ticks=tick, completion_ticks=[completed[i] for i in range(len(lengths))],
                trace=trace, tokens_per_tick=sum(lengths) / tick if tick else 0.)


def serving(seed=42):
    lengths = [2, 8, 2, 2, 6, 3]
    static = simulate(lengths, continuous=False)
    continuous = simulate(lengths, continuous=True)
    return dict(lengths=lengths, slots=2, static=static, continuous=continuous,
                note='Abstract ticks; no prefill/KV admission/real kernel cost; not a vLLM reproduction')


DOCS = [
    ('D1', 'KV Cache', 'KV Cache 缓存历史 token 的键和值，减少自回归推理的重复投影计算，但需要额外内存。'),
    ('D2', '量化', '量化使用 scale 和 zero point 将浮点值映射为低位宽整数。校准数据应代表部署输入分布。'),
    ('D3', 'ONNX', 'ONNX 描述计算图和张量。导出后仍需检查算子、输入形状、预处理与 Runtime 数值一致性。'),
    ('D4', 'FlashAttention', 'FlashAttention 通过分块与在线 softmax 减少中间矩阵的显存读写，不省略标准注意力的两两交互。'),
    ('D5', 'RKNN', 'RKNN 是 Rockchip 神经网络部署工具链。转换产物、Runtime 和驱动需要验证兼容性。'),
    ('D6', 'TTFT', 'TTFT 是从提交请求到第一个输出 token 的时间，包含排队、预处理与 prefill 等阶段。'),
    ('D7', 'Agent', 'Agent 可以提出工具调用。应用需要检查工具白名单、参数和调用次数，工具输出应视为数据。'),
]


def terms(text):
    ascii_terms = re.findall(r'[a-z0-9]+', text.lower())
    chinese_runs = re.findall(r'[\u4e00-\u9fff]+', text)
    return ascii_terms + [s[i:i+2] for s in chinese_runs for i in range(len(s)-1)]


def retrieve(query, k=2):
    """TF-IDF cosine baseline. Index corpus only; never fits IDF on test questions."""
    docs = [terms(title + ' ' + body) for _, title, body in DOCS]
    vocab = sorted(set(t for doc in docs for t in doc))
    df = Counter(t for doc in docs for t in set(doc))
    idf = np.array([math.log((1+len(docs))/(1+df[t]))+1 for t in vocab])
    def vector(tokens):
        c = Counter(tokens)
        v = np.array([c[t] for t in vocab]) * idf
        return v / max(np.linalg.norm(v), 1e-12)
    q = vector(terms(query))
    scores = np.array([vector(doc) @ q for doc in docs])
    order = np.argsort(-scores, kind='stable')[:k]
    return [dict(id=DOCS[i][0], title=DOCS[i][1], text=DOCS[i][2], score=float(scores[i]))
            for i in order if scores[i] > 0]


def call_tool(name, arguments, calls_so_far=0):
    if calls_so_far >= 3:
        raise ValueError('Tool budget exhausted')
    if name != 'get_model_info':
        raise ValueError('Tool not in allowlist')
    if not isinstance(arguments, dict) or set(arguments) != {'model_id'}:
        raise ValueError('Expected exactly model_id')
    if arguments['model_id'] != 'toy-mlp-v1':
        raise ValueError('Unknown model_id')
    return dict(model_id='toy-mlp-v1', input_features=4, runtime='CPU', source='local registry')


def rag(seed=42):
    questions = [('KV Cache 为什么占内存？', 'D1'), ('量化校准数据怎么选？', 'D2'),
                 ('ONNX 导出后怎样验证？', 'D3'), ('TTFT 是什么？', 'D6')]
    hits = [retrieve(q, 2) for q, _ in questions]
    recall = sum(any(d['id'] == expected for d in h) for h, (_, expected) in zip(hits, questions)) / len(questions)
    rejected = False
    try:
        call_tool('run_shell', {'command': 'do-something'})
    except ValueError:
        rejected = True
    return dict(recall_at_2=recall, num_questions=len(questions), example=hits[0],
                out_of_domain_abstains=not retrieve('海豚如何睡眠'),
                allowed_tool_result=call_tool('get_model_info', {'model_id':'toy-mlp-v1'}),
                unknown_tool_rejected=rejected,
                note='Extractive retrieval and deterministic tool router, without an LLM; not full RAG generation')
