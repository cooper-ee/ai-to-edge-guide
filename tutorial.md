# 源码课程与完整学习入口

用途：用可运行实验学习 AI 模型从训练到部署的完整过程。代码快照为本项目 v1.0；交付文件指纹见 `reports/file-manifest.json`。运行环境和测量范围见 [验证记录](reports/README.md)。

前置：Python 模块/环境、矩阵乘法和基础导数；不熟悉时从第 00 课补起。正文均为已展开课程。外部 Runtime、GPU/NPU 与多模态硬件部分是学习手册/适配模板，尚未在本交付验证，不补造调用链或性能。

建议先走 [学习路线](docs/roadmap.md)；完整章节和配套理解题如下。源码位于当前仓库，外部 API 必须按其固定版本核查。

## 00 · 先搭一张能用于排错的地图

- 状态：已展开。正文：[第 00 课](docs/00-foundations.md)。
- 读完回答：一个实验如何从命令行走到报告？
- 主链：CLI → main → run → 实验函数 → JSON。
- 阅读顺序：edge_ai_labs/__main__.py::main / run。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 01 · 机器学习：先证明模型学到了可迁移的规律

- 状态：已展开。正文：[第 01 课](docs/01-machine-learning.md)。
- 读完回答：训练、验证和测试各自参与了哪些决定？
- 主链：合成数据 → 划分 → 训练集拟合标准化 → 梯度更新 → 验证选模 → 测试。
- 阅读顺序：edge_ai_labs/math_labs.py::ml。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 02 · 神经网络：把学参数拆成四步

- 状态：已展开。正文：[第 02 课](docs/02-neural-networks.md)。
- 读完回答：梯度是否正确，参数何时更新？
- 主链：解析/有限差分对照 → MLP 前向 → loss → backward → step → checkpoint。
- 阅读顺序：edge_ai_labs/math_labs.py::gradients; edge_ai_labs/torch_labs.py::classifier / model_class。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 03 · 模型交付：导出成功只是第一道门

- 状态：已展开。正文：[第 03 课](docs/03-export-and-correctness.md)。
- 读完回答：图合法之外，还如何证明转换前后语义一致？
- 主链：checkpoint → Pipeline → ONNX exporter → checker → ORT → 多batch/任务对照。
- 阅读顺序：edge_ai_labs/torch_labs.py::export / load_classifier。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 04 · Transformer：按张量形状理解注意力

- 状态：已展开。正文：[第 04 课](docs/04-transformer.md)。
- 读完回答：一个token如何从ID变成logits？
- 主链：字符ID → embedding/position → LN/QKV → mask/softmax → residual/FFN → logits。
- 阅读顺序：edge_ai_labs/math_labs.py::dense_attention; edge_ai_labs/torch_labs.py::tiny_lm / TinyLM.forward。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 05 · LLM推理：用时间线和内存账理解快慢

- 状态：已展开。正文：[第 05 课](docs/05-inference-and-cache.md)。
- 读完回答：cache为什么有效，为什么会占额外内存？
- 主链：prefill → 保存KV → 当前token/offset → 追加KV → 对照完整前向。
- 阅读顺序：edge_ai_labs/math_labs.py::kv_bytes; edge_ai_labs/torch_labs.py::TinyLM.forward。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 06 · 量化：误差、存储和执行

- 状态：已展开。正文：[第 06 课](docs/06-quantization.md)。
- 读完回答：降低位宽改变了哪些东西？
- 主链：范围 → scale → round/clip → 重建 → 权重/输出MSE对照。
- 阅读顺序：edge_ai_labs/math_labs.py::quantize_dequantize / quantization。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 07 · RAG与Agent：知识从哪里来，动作由谁执行

- 状态：已展开。正文：[第 07 课](docs/07-rag-and-agent.md)。
- 读完回答：证据如何被找到，工具建议如何被接受或拒绝？
- 主链：文档词项/IDF → query余弦检索 → 文档ID → 命中评估；工具名/参数/预算校验。
- 阅读顺序：edge_ai_labs/systems.py::rag / retrieve / call_tool。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 08 · llama.cpp：真实本地语言模型

- 状态：已展开。正文：[第 08 课](docs/08-llama-cpp.md)。
- 读完回答：模型文件、上下文与执行后端怎样连接？
- 主链：固定checkout → 核验GGUF → 加载 → 上下文 → decode → logits/采样（外部待测）。
- 阅读顺序：edge_ai_labs/torch_labs.py::tiny_lm；外部源码按docs/08中的rg命令定位。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 09 · Serving：从能生成到多人同时用

- 状态：已展开。正文：[第 09 课](docs/09-serving-and-runtimes.md)。
- 读完回答：为什么空出的执行槽有时可以接新请求？
- 主链：请求队列 → 补位 → 当前轮token → 完成记录 → 移除 → 下一轮。
- 阅读顺序：edge_ai_labs/systems.py::simulate / serving。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 10 · AI编译器：计算不变，安排可以不同

- 状态：已展开。正文：[第 10 课](docs/10-compiler.md)。
- 读完回答：同一矩阵乘为何可以有不同数据搬运？
- 主链：构造矩阵 → tile遍历/尾块 → 累加 → NumPy参考对照 → Roofline估算。
- 阅读顺序：edge_ai_labs/math_labs.py::compiler。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 11 · GPU Kernel与FlashAttention：少搬中间结果

- 状态：已展开。正文：[第 11 课](docs/11-kernel-and-flashattention.md)。
- 读完回答：不保存完整scores，如何保留相同归一化？
- 主链：key分块 → 更新最大值 → 重标定旧状态 → 累加新块 → a/denom。
- 阅读顺序：edge_ai_labs/math_labs.py::dense_attention / online_attention; tests/test_invariants.py。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 12 · RKNN与NPU：把兼容性当完整链路检查

- 状态：已展开。正文：[第 12 课](docs/12-rknn.md)。
- 读完回答：Host完成转换之后，还缺哪些证据？
- 主链：checkpoint → 静态ONNX → Toolkit转换模板 → artifact/hash → Board对照（待测）。
- 阅读顺序：adapters/export_static.py::main; adapters/convert_rknn.py::main / check。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 13 · RKLLM：产物、状态与生命周期

- 状态：已展开。正文：[第 13 课](docs/13-rkllm.md)。
- 读完回答：会话、回调与取消时谁拥有资源？
- 主链：固定模型/SDK → 官方基线 → 产物校验 → 初始化 → 生成 → 确认结束 → 释放（待测）。
- 阅读顺序：本仓库无RKLLM运行实现；以docs/13的固定SDK头文件/官方示例为边界。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 14 · Linux与系统集成：可观测服务

- 状态：已展开。正文：[第 14 课](docs/14-linux-and-integration.md)。
- 读完回答：原始HTTP输入如何变成可追溯输出？
- 主链：启动加载模型 → 校验body/schema/shape → 标准化/预测 → JSON/hash；错误返回400/404。
- 阅读顺序：edge_ai_labs/serve.py::build_server / Handler.do_GET / Handler.do_POST。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 15 · 基准与排错：用证据决定优化方向

- 状态：已展开。正文：[第 15 课](docs/15-benchmark-and-debug.md)。
- 读完回答：计时究竟包含哪些工作？
- 主链：加载 → 固定输入 → 预热 → 重复forward计时 → 原始数组 → p50/p95/吞吐。
- 阅读顺序：scripts/benchmark.py::main; tests/test_invariants.py::ServiceIntegration。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 16 · 综合项目：可复现作品

- 状态：已展开。正文：[第 16 课](docs/16-capstone.md)。
- 读完回答：别人能否独立复现你的结论？
- 主链：训练 → 导出 → 数值/任务对照 → HTTP → 测试 → 原始基准 → 报告。
- 阅读顺序：edge_ai_labs/__main__.py::main; scripts/benchmark.py; edge_ai_labs/serve.py。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

## 17 · 进阶：混合注意力与多模态解剖

- 状态：已展开。正文：[第 17 课](docs/17-model-anatomy.md)。
- 读完回答：为什么24层模型不能都套标准KV公式？
- 主链：核查config → 分离层类型 → full-KV估算 → 其它状态单列 → 上下文扫描计划。
- 阅读顺序：edge_ai_labs/math_labs.py::kv_bytes；真实配置入口见docs/17。按上述输入到输出次序定位。
- 验证证据：正文实验与 `tests/test_invariants.py`；外部硬件按正文状态说明。
- 暂缓范围：相邻主题按章节归属阅读；本课不补造未实现的外部行为。

