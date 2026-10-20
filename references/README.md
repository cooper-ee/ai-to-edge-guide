# 可核查论文与官方资料

资料入口核查日期：2026-10-19。论文按作者、年份、标题、发表载体列出，并给原文/PDF；软件文档是可变入口，实际实验必须另记 release/commit。正文推导是本项目的教学展开，不宣称提出原算法。

## 原论文

| ID | 引用信息 | 原文与 PDF | 本教程用在哪里 |
|---|---|---|---|
| P01 | Vaswani, A., et al. (2017). **Attention Is All You Need**. NeurIPS. | [记录](https://arxiv.org/abs/1706.03762) · [PDF](https://arxiv.org/pdf/1706.03762) | attention、multi-head、因果遮罩 |
| P02 | Dao, T., Fu, D. Y., Ermon, S., Rudra, A., & Ré, C. (2022). **FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness**. NeurIPS. | [记录](https://arxiv.org/abs/2205.14135) · [PDF](https://arxiv.org/pdf/2205.14135) | IO-aware 分块与在线归一化 |
| P03 | Kwon, W., et al. (2023). **Efficient Memory Management for Large Language Model Serving with PagedAttention**. SOSP. | [记录](https://arxiv.org/abs/2309.06180) · [PDF](https://arxiv.org/pdf/2309.06180) | 分页 KV 与 serving |
| P04 | Ainslie, J., et al. (2023). **GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints**. EMNLP. | [记录](https://arxiv.org/abs/2305.13245) · [PDF](https://arxiv.org/pdf/2305.13245) | query 头与 KV 头分组 |
| P05 | Shazeer, N. (2019). **Fast Transformer Decoding: One Write-Head is All You Need**. arXiv preprint. | [记录](https://arxiv.org/abs/1911.02150) · [PDF](https://arxiv.org/pdf/1911.02150) | MQA 与解码访存背景 |
| P06 | Jacob, B., et al. (2018). **Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference**. CVPR. | [记录](https://arxiv.org/abs/1712.05877) · [PDF](https://arxiv.org/pdf/1712.05877) | 仿射量化、整数推理 |
| P07 | Lin, J., et al. (2024). **AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration**. MLSys. | [记录](https://arxiv.org/abs/2306.00978) · [PDF](https://arxiv.org/pdf/2306.00978) | 扩展阅读；代码没有实现 AWQ |
| P08 | Lewis, P., et al. (2020). **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks**. NeurIPS. | [记录](https://arxiv.org/abs/2005.11401) · [PDF](https://arxiv.org/pdf/2005.11401) | 检索与生成结合 |
| P09 | Yao, S., et al. (2023). **ReAct: Synergizing Reasoning and Acting in Language Models**. ICLR. | [记录](https://arxiv.org/abs/2210.03629) · [PDF](https://arxiv.org/pdf/2210.03629) | 推理/行动循环背景 |
| P10 | Chen, T., et al. (2018). **TVM: An Automated End-to-End Optimizing Compiler for Deep Learning**. OSDI. | [记录](https://arxiv.org/abs/1802.04799) · [PDF](https://arxiv.org/pdf/1802.04799) | 编译器分层与硬件适配 |
| P11 | Williams, S., Waterman, A., & Patterson, D. (2009). **Roofline: An Insightful Visual Performance Model for Multicore Architectures**. Communications of the ACM, 52(4), 65–76. DOI: 10.1145/1498765.1498785. | [作者实验室出版目录](https://amcr.lbl.gov/departments/computer-science-department/ppan/roofline-performance-model/ppan-roofline-publications/) · [作者技术报告 PDF，2008 版](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2008/EECS-2008-134.pdf) | 算术强度与计算/带宽上限 |

BibTeX 文件见 [papers.bib](papers.bib)。P11 的下载版是先行技术报告，标题含 Floating-Point Programs，与 2009 年期刊标题略有不同，已分开说明，不冒充同一排版版本。

## 官方文档与代码

| 主题 | 一手来源 | 使用注意 |
|---|---|---|
| 基础教材 | [Dive into Deep Learning](https://d2l.ai/) | 作为拓展教材，按所读版本学习 |
| 自动求导 | [PyTorch autograd 教程](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html) | 区分求梯度与优化器更新 |
| 可复现性 | [PyTorch randomness](https://docs.pytorch.org/docs/stable/notes/randomness.html) | seed 不保证跨版本/平台逐位相同 |
| ONNX 导出 | [PyTorch exporter](https://docs.pytorch.org/docs/stable/onnx_export.html) | 新版 dynamo/shape 参数需匹配版本 |
| Runtime | [ONNX Runtime](https://onnxruntime.ai/docs/) | 按模型检查 Execution Provider 支持 |
| 量化 | [ORT quantization](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html) | 看校准、数据类型与设备约束 |
| 本地 LLM | [llama.cpp](https://github.com/ggml-org/llama.cpp) · [构建文档](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md) | 保存 commit 和工具 help |
| 小模型示例 | [Qwen2.5-0.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF) | 下载具体文件并固定 revision/hash |
| Serving | [vLLM](https://docs.vllm.ai/en/latest/) · [PagedAttention 文档](https://docs.vllm.ai/en/latest/design/paged_attention/) | 历史论文思想与当前实现分别核查 |
| 编译部署 | [MLC Python API](https://llm.mlc.ai/docs/deploy/python_engine.html) | 模型库、权重与目标要匹配 |
| 编译器 | [TVM 文档](https://tvm.apache.org/docs/index.html) · [Relax](https://tvm.apache.org/docs/deep_dive/relax/index.html) · [TensorIR](https://tvm.apache.org/docs/deep_dive/tensor_ir/index.html) | 旧文章不能锁定当前 import/API |
| GPU | [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/index.html) · [Triton Fused Attention](https://triton-lang.org/main/getting-started/tutorials/06-fused-attention.html) | 数学等价不等于硬件性能复现 |
| NPU | [RKNN-Toolkit2](https://github.com/airockchip/rknn-toolkit2) · [Model Zoo](https://github.com/airockchip/rknn_model_zoo) | 查所选 release 支持矩阵 |
| 端侧 LLM | [rknn-llm](https://github.com/airockchip/rknn-llm) | 不猜厂商算法内部数学 |
| 混合模型配置 | [Qwen3.5-2B config](https://huggingface.co/Qwen/Qwen3.5-2B/blob/main/config.json) | 只把配置可证实的字段当事实 |
| 工具协议 | [MCP 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18) | 协议支持不替代应用授权 |

## 版权与分发

本项目未重新分发第三方论文 PDF、图片或模型权重。第三方组件许可集中保存在 [许可声明](../licenses/THIRD_PARTY_NOTICES.txt) 与 `vendor/`，学术引用按上述原论文标注。
