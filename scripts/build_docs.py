"""Build course navigation, exercises and an optional consolidated HTML reader."""
from pathlib import Path
import html
import os
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
# id, slug, title, real source locations, scenario/question, flow, exercises
COURSES = [
('00','foundations','先搭一张能用于排错的地图','edge_ai_labs/__main__.py::main / run',
 '一个实验如何从命令行走到报告？','CLI → main → run → 实验函数 → JSON',
 ['区分模型结构、权重、格式、Runtime、编译器和 Kernel。','解释为什么在另一个目录运行会找不到模块，并给出环境核查步骤。']),
('01','machine-learning','机器学习：先证明模型学到了可迁移的规律','edge_ai_labs/math_labs.py::ml',
 '训练、验证和测试各自参与了哪些决定？','合成数据 → 划分 → 训练集拟合标准化 → 梯度更新 → 验证选模 → 测试',
 ['从似然推出二元交叉熵与逻辑回归梯度，检查更新符号。','给出随机切分会泄漏的一个时序或分组例子，解释替代切分。']),
('02','neural-networks','神经网络：把学参数拆成四步','edge_ai_labs/math_labs.py::gradients; edge_ai_labs/torch_labs.py::classifier / model_class',
 '梯度是否正确，参数何时更新？','解析/有限差分对照 → MLP 前向 → loss → backward → step → checkpoint',
 ['解释连续线性层为何仍能合并为一个仿射层。','逐项计算114参数，并解释eval、inference_mode、zero_grad的职责。']),
('03','export-and-correctness','模型交付：导出成功只是第一道门','edge_ai_labs/torch_labs.py::export / load_classifier',
 '图合法之外，还如何证明转换前后语义一致？','checkpoint → Pipeline → ONNX exporter → checker → ORT → 多batch/任务对照',
 ['写出绝对/相对容差条件，讨论参考值接近零的情况。','为什么本例把标准化register_buffer进图？实际测试哪些batch？']),
('04','transformer','Transformer：按张量形状理解注意力','edge_ai_labs/math_labs.py::dense_attention; edge_ai_labs/torch_labs.py::tiny_lm / TinyLM.forward',
 '一个token如何从ID变成logits？','字符ID → embedding/position → LN/QKV → mask/softmax → residual/FFN → logits',
 ['写出B=2,H=4,T=8,dh=8时各张量shape，并指出softmax轴。','从独立单位方差假设解释除以sqrt(dk)，并说明假设边界。']),
('05','inference-and-cache','LLM推理：用时间线和内存账理解快慢','edge_ai_labs/math_labs.py::kv_bytes; edge_ai_labs/torch_labs.py::TinyLM.forward',
 'cache为什么有效，为什么会占额外内存？','prefill → 保存KV → 当前token/offset → 追加KV → 对照完整前向',
 ['从缓存shape推出KV字节公式，并把合成配置结果换算为MiB。','若decode每次position从0开始，会发生什么？如何做独立检查？']),
('06','quantization','量化：误差、存储和执行','edge_ai_labs/math_labs.py::quantize_dequantize / quantization',
 '降低位宽改变了哪些东西？','范围 → scale → round/clip → 重建 → 权重/输出MSE对照',
 ['为[-0.2,0.1,0.2,30]手算INT4共享scale，解释小值损失。','解释为什么裁剪未必有益、ideal_weight_bytes不是实际文件大小。']),
('07','rag-and-agent','RAG与Agent：知识从哪里来，动作由谁执行','edge_ai_labs/systems.py::rag / retrieve / call_tool',
 '证据如何被找到，工具建议如何被接受或拒绝？','文档词项/IDF → query余弦检索 → 文档ID → 命中评估；工具名/参数/预算校验',
 ['解释四题Recall@2=1为什么不足以证明真实RAG质量。','给出一个词相似但结论相反的文档，说明检索与引用核查分工。']),
('08','llama-cpp','llama.cpp：真实本地语言模型','edge_ai_labs/torch_labs.py::tiny_lm；外部源码按docs/08中的rg命令定位',
 '模型文件、上下文与执行后端怎样连接？','固定checkout → 核验GGUF → 加载 → 上下文 → decode → logits/采样（外部待测）',
 ['区分GGUF、量化类型、模型权重与会话状态。','列出一份可复现实验必需的版本、hash、模板与计时证据。']),
('09','serving-and-runtimes','Serving：从能生成到多人同时用','edge_ai_labs/systems.py::simulate / serving',
 '为什么空出的执行槽有时可以接新请求？','请求队列 → 补位 → 当前轮token → 完成记录 → 移除 → 下一轮',
 ['对默认长度手画两种trace，并验证总token数守恒。','说明tick模拟未建模哪些成本；为什么不能宣称vLLM实测提速？']),
('10','compiler','AI编译器：计算不变，安排可以不同','edge_ai_labs/math_labs.py::compiler',
 '同一矩阵乘为何可以有不同数据搬运？','构造矩阵 → tile遍历/尾块 → 累加 → NumPy参考对照 → Roofline估算',
 ['推导一个b×b块的近似算术强度，并说明忽略了什么。','解释融合为何可能减少写回却不保证更快。']),
('11','kernel-and-flashattention','GPU Kernel与FlashAttention：少搬中间结果','edge_ai_labs/math_labs.py::dense_attention / online_attention; tests/test_invariants.py',
 '不保存完整scores，如何保留相同归一化？','key分块 → 更新最大值 → 重标定旧状态 → 累加新块 → a/denom',
 ['从指数恒等式推出rescale，并手算[1,2]与value[10,20]。','解释块大小为1、不能整除尾块和大logits分别在检查什么。']),
('12','rknn','RKNN与NPU：把兼容性当完整链路检查','adapters/export_static.py::main; adapters/convert_rknn.py::main / check',
 'Host完成转换之后，还缺哪些证据？','checkpoint → 静态ONNX → Toolkit转换模板 → artifact/hash → Board对照（待测）',
 ['解释图内标准化为何不能在Toolkit再配置一次。','写出PyTorch/ORT、转换工具、Board和真实业务的分层验收。']),
('13','rkllm','RKLLM：产物、状态与生命周期','本仓库无RKLLM运行实现；以docs/13的固定SDK头文件/官方示例为边界',
 '会话、回调与取消时谁拥有资源？','固定模型/SDK → 官方基线 → 产物校验 → 初始化 → 生成 → 确认结束 → 释放（待测）',
 ['画初始化失败、正常完成、用户取消三条资源路径。','说明为什么不能根据GRQ缩写猜算法，也不能把W4A16当全部内存位宽。']),
('14','linux-and-integration','Linux与系统集成：可观测服务','edge_ai_labs/serve.py::build_server / Handler.do_GET / Handler.do_POST',
 '原始HTTP输入如何变成可追溯输出？','启动加载模型 → 校验body/schema/shape → 标准化/预测 → JSON/hash；错误返回400/404',
 ['从客户端断开推导为什么底层生成未必已取消。','为30FPS采集、5FPS处理设计有界队列，并说明业务取舍。']),
('15','benchmark-and-debug','基准与排错：用证据决定优化方向','scripts/benchmark.py::main; tests/test_invariants.py::ServiceIntegration',
 '计时究竟包含哪些工作？','加载 → 固定输入 → 预热 → 重复forward计时 → 原始数组 → p50/p95/吞吐',
 ['区分batch延迟、单样本摊销时间和单请求延迟。','用Amdahl解释计算占40%时无限加速的端到端上限。']),
('16','capstone','综合项目：可复现作品','edge_ai_labs/__main__.py::main; scripts/benchmark.py; edge_ai_labs/serve.py',
 '别人能否独立复现你的结论？','训练 → 导出 → 数值/任务对照 → HTTP → 测试 → 原始基准 → 报告',
 ['按观察、假设、对照、结论写一个自己的扩展计划。','分别列出项目A已实现、项目B与C待实现的边界。']),
('17','model-anatomy','进阶：混合注意力与多模态解剖','edge_ai_labs/math_labs.py::kv_bytes；真实配置入口见docs/17',
 '为什么24层模型不能都套标准KV公式？','核查config → 分离层类型 → full-KV估算 → 其它状态单列 → 上下文扫描计划',
 ['用6层、2个KV头、dh=256、T=2048、2字节算24MiB并复核。','把配置事实、估算假设和必须实测的行为各列三项。']),
]


def build_navigation():
    intro='''# 源码课程与完整学习入口

用途：用可运行实验学习 AI 模型从训练到部署的完整过程。代码快照为本项目 v1.0；交付文件指纹见 `reports/file-manifest.json`。运行环境和测量范围见 [验证记录](reports/README.md)。

前置：Python 模块/环境、矩阵乘法和基础导数；不熟悉时从第 00 课补起。正文均为已展开课程。外部 Runtime、GPU/NPU 与多模态硬件部分是学习手册/适配模板，尚未在本交付验证，不补造调用链或性能。

建议先走 [学习路线](docs/roadmap.md)；完整章节和配套理解题如下。源码位于当前仓库，外部 API 必须按其固定版本核查。

'''
    practice='# 配套理解与扩展练习\n\n每课对应已展开正文。先自己推导和复述，再用源码/实验核对。此文件不附标准答案；正文中的可检查结果用于自我验收。\n\n'
    for n,slug,title,source,q,flow,exercises in COURSES:
        file=f'docs/{n}-{slug}.md'
        intro+=f'## {n} · {title}\n\n- 状态：已展开。正文：[第 {n} 课]({file})。\n- 读完回答：{q}\n- 主链：{flow}。\n- 阅读顺序：{source}。按上述输入到输出次序定位。\n- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。\n- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。\n\n'
        practice+=f'## {n} · {title}\n\n对应：[已展开正文]({file})。\n\n'
        for i,ex in enumerate(exercises,1):practice+=f'{i}. {ex}\n'
        practice+='\n复述要求：给输入、关键状态、输出和适用边界；涉及本仓库实现时引用具体文件与函数。\n\n'
    (ROOT/'tutorial.md').write_text(intro,encoding='utf8')
    (ROOT/'practice.md').write_text(practice,encoding='utf8')


def html_body(source,base):
    import markdown
    math = []
    def stash(m):
        math.append(m.group(0))
        return f'ZZMATHPLACEHOLDER{len(math)-1}ZZ'
    # Preserve raw LaTeX before Markdown interprets underscores/backslashes.
    source = re.sub(r'\$\$[\s\S]*?\$\$|(?<!\$)\$(?!\$)[^\n$]+?\$(?!\$)',stash,source)
    body=markdown.markdown(source,extensions=['tables','fenced_code'])
    for i,s in enumerate(math):body=body.replace(f'ZZMATHPLACEHOLDER{i}ZZ',html.escape(s))
    def relocate(match):
        attr,value=match.groups()
        if value.startswith('#') or urlsplit(value).scheme:
            return match.group(0)
        target,mark,anchor=value.partition('#')
        relative=os.path.relpath(base/target,ROOT).replace('\\','/')
        return f'{attr}="{relative}{mark}{anchor}"'
    body=re.sub(r'(href|src)="([^"]+)"',relocate,body)
    # Provide a readable fold for Mermaid source; static SVGs cover the main routes.
    body=re.sub(r'<pre><code class="language-mermaid">([\s\S]*?)</code></pre>',r'<details><summary>流程图源代码（GitHub 中可直接渲染）</summary><pre><code>\1</code></pre></details>',body)
    return body


def build_reader():
    chapters=[('roadmap','学习路线',ROOT/'docs/roadmap.md')]
    chapters += [(f'c{n}',f'{n} {title}',ROOT/f'docs/{n}-{slug}.md') for n,slug,title,*_ in COURSES]
    chapters += [('knowledge','知识体系',ROOT/'docs/knowledge-map.md'),('decisions','理解与取舍',ROOT/'docs/understanding-and-decisions.md'),('references','论文与官方资料',ROOT/'references/README.md')]
    nav=''.join(f'<a href="#{id}">{html.escape(title)}</a>' for id,title,_ in chapters)
    body=''.join(f'<article id="{id}">{html_body(p.read_text(encoding="utf8"),p.parent)}</article>' for id,_,p in chapters)
    css='''*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:30px}body{margin:0;background:#f5f8fa;color:#183548;font:16px/1.95 "Segoe UI","Microsoft YaHei",sans-serif}aside{position:fixed;inset:0 auto 0 0;width:275px;overflow:auto;padding:24px 20px;background:#102f42;color:#cae0ea}aside>a{display:block;font-size:12px;padding:7px 0;border-bottom:1px solid #284858}aside .logo{font-size:20px;font-weight:700;margin-bottom:22px;color:#7bd5d1}main{max-width:1150px;margin:0 auto 0 295px;padding:35px 50px}article{background:white;border:1px solid #dce6eb;border-radius:14px;padding:35px 42px;margin-bottom:32px;overflow-wrap:anywhere}h1{font-size:29px;line-height:1.5}h2{font-size:23px;margin-top:35px;color:#087d81}h3{font-size:19px}a{color:#087d81;text-decoration:none}aside a{color:#cae0ea}img{max-width:100%;height:auto}pre{background:#edf3f6;padding:18px;border-radius:8px;overflow:auto;font-size:13px;line-height:1.8}code{font-family:Consolas,monospace;font-size:.9em}table{border-collapse:collapse;width:100%;font-size:13px;display:block;overflow:auto}th,td{border:1px solid #dce5eb;text-align:left;padding:10px}th{background:#edf5f6}blockquote{border-left:3px solid #07878b;padding-left:17px;color:#59707d;margin-left:0}.note{color:#5e7584;font-size:12px;padding:0 5px 20px}summary{cursor:pointer;color:#67808e;font-size:12px}mjx-container[display=true]{overflow-x:auto;overflow-y:hidden;padding:10px 0}@media(max-width:900px){aside{position:static;width:auto;max-height:220px}main{margin:0;padding:20px}article{padding:22px}h1{font-size:25px}}@media print{aside,.note{display:none}main{margin:0;padding:0}article{border:0;page-break-before:always}}'''
    head='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>完整教程 · AI to Edge</title><style>'''+css+'''</style><script>window.MathJax={tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']]},options:{skipHtmlTags:['script','noscript','style','textarea','pre','code']}};</script><script defer src="vendor/mathjax/tex-svg.js"></script></head><body>'''
    page=head+'<aside><a class="logo" href="index.html">← AI / EDGE 实验台</a>'+nav+'</aside><main><p class="note">正文与公式均可离线阅读；流程图源在 GitHub 可渲染，主线另附 SVG。MathJax 许可见 vendor/mathjax/LICENSE。</p>'+body+'</main></body></html>'
    (ROOT/'reader.html').write_text(page,encoding='utf8')


def add_chapter_navigation():
    for i,(n,slug,title,*_) in enumerate(COURSES):
        p=ROOT/f'docs/{n}-{slug}.md'
        body=p.read_text(encoding='utf8').split('\n<!-- COURSE-NAV -->')[0].rstrip()
        nav=['[路线总览](roadmap.md)','[课程与源码](../tutorial.md)','[配套练习](../practice.md)']
        if i:
            prev=COURSES[i-1];nav.append(f'[上一课 {prev[0]}]({prev[0]}-{prev[1]}.md)')
        if i+1<len(COURSES):
            nxt=COURSES[i+1];nav.append(f'[下一课 {nxt[0]}]({nxt[0]}-{nxt[1]}.md)')
        p.write_text(body+'\n\n<!-- COURSE-NAV -->\n\n---\n\n'+' · '.join(nav)+'\n',encoding='utf8')


if __name__ == '__main__':
    build_navigation()
    add_chapter_navigation()
    build_reader()
    print('Built tutorial.md, practice.md, reader.html and chapter navigation')
