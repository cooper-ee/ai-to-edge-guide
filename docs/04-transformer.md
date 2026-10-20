# 04 · Transformer：按张量形状理解注意力

> 状态：已展开。目标：手算一个 attention，并训练可检查的微型语言模型。前置：第 02 课；第 03 课可后补。

## 本课结论

注意力是“依据当前问题，从已有信息中加权读取内容”的可微操作。它不自动理解语言；参数、数据、训练目标和结构共同决定最后学到什么。

假设你在读“把书放到桌上，因为它很平”。要理解“它”，你会回头比较候选对象。注意力中的 query 像当前要找的线索，key 像每个位置提供的索引，value 才是最后取回并混合的信息。这个比喻帮助理解数据流，但 attention 权重不能直接当作可靠的因果解释。

## 从输入到输出，逐项核对 shape

令 $`X\in\mathbb R^{T\times d}`$，单头投影：

```math
Q=XW_Q\in\mathbb R^{T\times d_k},\quad
K=XW_K\in\mathbb R^{T\times d_k},\quad
V=XW_V\in\mathbb R^{T\times d_v}.
```


```math
S=QK^\top/\sqrt{d_k},\qquad P=\mathrm{softmax}(S+M),\qquad O=PV.
```


$`S`$、$`P`$ 是 $`T\times T`$，$`O`$ 是 $`T\times d_v`$。softmax 沿 key 轴进行，每一行权重和为 1。不能误沿 query 轴归一化。[Vaswani 等，2017，NeurIPS，原文 PDF](https://arxiv.org/pdf/1706.03762)

为什么除以 $`\sqrt{d_k}`$？若 query 与 key 各分量近似独立、均值为零、方差为 1，内积方差约为 $`d_k`$。缩放让打分的尺度不随维度直接膨胀，缓解 softmax 过度饱和。这是初始化尺度下的解释，不是训练后严格分布不变的保证。

对 $`T=3`$ 的自回归输入，因果遮罩为：

```math
M=\begin{bmatrix}0&-\infty&-\infty\\0&0&-\infty\\0&0&0\end{bmatrix}.
```


第 0 个位置只看自身，第 1 个位置看前两个，最后一个位置可以看全部。未来位置不是权重较小，而是被排除。修改未来 token 后，前面的输出应保持不变，这比肉眼看图更可靠。

![因果注意力动画](../assets/attention.gif)

## 多头、GQA 与完整 Block

多头把表示分成多个子空间。常见 shape 为 $`[B,H,T,d_h]`$，各头输出拼接后经过输出投影。GQA 中 query 头数 $`H_q`$ 大于 KV 头数 $`H_{kv}`$，每组 query 共享 KV。它减少 KV 存储和读取，但属于模型结构选择；不能把任意训练好的 MHA 权重随意删成 GQA 而假定语义不变。[Ainslie 等，2023，EMNLP，GQA](https://arxiv.org/pdf/2305.13245)

本项目采用一个 pre-norm block：

```math
U=X+\mathrm{Attention}(\mathrm{LN}(X)),\qquad
Y=U+\mathrm{FFN}(\mathrm{LN}(U)).
```


残差让信息和梯度有较直接的通路；归一化控制特征尺度；FFN 在每个位置上做非线性变换。现代 LLM 可能采用 RMSNorm、SwiGLU、RoPE、门控等变体。入门时先掌握数据流，再对照具体 config，别把一种实现当作全部 Transformer。

## 语言模型到底训练什么

自回归分解为 $`p(x_{1:T})=\prod_t p(x_t\mid x_{\lt t})`$，训练损失通常是各预测位置的交叉熵。已知整段文本时，可用遮罩同时计算多个位置的训练损失；生成时下一 token 未知，要逐步采样。训练的并行不等于生成没有依赖。

Tokenizer 把文本变成 token ID，embedding 把 ID 变成可训练向量。词表、特殊 token 和 chat template 都属于模型契约。字符数、词数、token 数不能互换。本项目微型模型使用字符词表，避免把 tokenizer 库安装变成学习障碍。

## 实验、调用链与边界

```powershell
python -m edge_ai_labs --lab attention
python -m edge_ai_labs --lab tiny-lm --seed 42
```

1. `math_labs.py::attention`：产生 $`Q,K,V`$，比较完整因果 attention 与逐 token 读取历史 KV。
2. `torch_labs.py::tiny_lm`：生成原创玩具语料和字符词表。
3. `TinyLM.forward`：token/position embedding → LN → QKV → mask/softmax → residual → FFN → logits。
4. 训练 100 步，再比较整段前向与“11 token prefill + 逐 token decode”。
5. 改写未来输入，验证前 20 个位置的 logits 不变。

模型只有约 1.6 万参数；默认训练损失下降，但生成文本仍会重复或拼错。语料重复、没有独立测试集，因此不能报告通用语言能力。这里验证的是训练链路、shape、cache 和因果约束。不要把训练损失当作下游质量结论。

过关任务：取 $`B=2,H=4,T=8,d_h=8`$，写出 Q、scores、输出以及缓存的 shape；解释为什么多个头并不等于四个独立大模型。下一课只研究已经存在的模型如何生成，不再展开预训练工程。

<!-- COURSE-NAV -->

---

[路线总览](roadmap.md) · [课程与源码](../tutorial.md) · [配套练习](../practice.md) · [上一课 03](03-export-and-correctness.md) · [下一课 05](05-inference-and-cache.md)
