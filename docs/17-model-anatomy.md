# 17 · 进阶：从 config 解剖混合注意力与多模态模型

> 状态：已展开。目标：避免用标准 Transformer 公式错误估算新架构。前置：第 04–06 课。只核查配置与理论，不宣称板端实测。

## 本课结论

模型名称里的参数规模不能代替结构配置。层类型、KV 头数、head dimension、视觉模块与运行状态必须逐项读取。混合架构尤其不能把“总层数”全放进标准 KV Cache 公式。

## 一个可核查的真实配置例子

核查入口：[Qwen/Qwen3.5-2B 官方 config](https://huggingface.co/Qwen/Qwen3.5-2B/blob/main/config.json)。可见文件提交短 ID 为 `999a2dd`，其内容包含文本与视觉配置。为避免 `main` 后续变化，正式实验应下载所用 revision 的配置并计算 hash。

这里仅使用对内存估算必要的配置事实：文本层数 24，其中 `layer_types` 包含 6 个 full attention 与 18 个 linear attention；full-attention 的 `num_key_value_heads=2`、`head_dim=256`。这些是**配置事实**，不是模型实际运行的全部内存分配行为。

## 重算 full-attention KV，而不是照抄标准模型

假设 batch=1，序列长度 2048，KV 元素用 2 字节：

$$M_{fullKV}=2\times6\times2048\times2\times256\times2
=25{,}165{,}824\ \mathrm{bytes}=24\ \mathrm{MiB}.$$

这里的 2 字节是估算假设，需与所用 Runtime 的 cache dtype 核对。把 24 层都当全注意力会算出 96 MiB；它不是这个配置的 full-attention KV payload。反过来，只报 24 MiB 为“总缓存”也不正确，因为另有线性层状态与 Runtime 开销。

可以用仓库的逐层函数复核：

```python
from edge_ai_labs.math_labs import kv_bytes
assert kv_bytes([6], [2], [256], tokens=2048, element_bytes=2) == 24 * 2**20
```

第 05 课的教学配置是 $H_{kv}=4,d_h=64$，所以结果不同。不能只改模型名称而保留旧例的数字。

## 线性注意力状态怎么理解

某些线性注意力可以示意为递推更新 $S_t=f(S_{t-1},k_t,v_t)$，读出 $o_t=g(q_t,S_t)$。在固定结构下，部分状态大小可能不随历史 token 数线性增长，但它的精度、头维度、短卷积状态、checkpoint 或分块策略仍会影响实际内存。

这个递推式只是抽象说明，**不是对 Qwen 具体线性注意力实现的完整公式**。不能据此推断门控更新、数值精度和内部 buffer 大小。要给精确公式，需继续核查对应模型实现与技术报告；SDK 未公开的内部处理保持未知。

大白话：全注意力像把所有历史条目逐条保留，递推状态像不断更新一张工作摘要。但“摘要”不等于所有信息无损、固定大小就一定更好，也不等于完全没有其它缓存。

## 多模态是对齐契约，不是额外传一个数组

典型视觉语言链路是图像 → resize/归一化/patch → vision encoder → projector/对齐 → 图像 token 或 embedding → 语言侧。需要核对维度、图像 token 数、位置规则、特殊 token、padding 和图像顺序。

模型目录里同时出现视觉和文本权重，不代表当前部署产物已经包含两者。转换器可能只导出语言侧；vision encoder 可能另走 RKNN；二者连接需要 SDK 支持和数值对照。先把“文本能生成”和“图像问答正确”作为两份验收。

## 如何用测量验证理论账本

固定产物、batch 与输出长度，扫描多个实际上下文长度，记录加载后、prefill 峰值、decode 和结束后的内存。将理论 full KV 斜率与实测增量比较。差额先记作“其他状态/分配开销”，只有逐项证据出现后再命名原因。

过关任务：写一张表，分别列“来自 config 的事实”“估算时的假设”“必须实测的行为”。原附件已正确强调混合层不能套全层 KV 公式；本版在此基础上增加了单位推导、与教学配置的区别和可执行校验。

<!-- COURSE-NAV -->

---

[路线总览](roadmap.md) · [课程与源码](../tutorial.md) · [配套练习](../practice.md) · [上一课 16](16-capstone.md)
