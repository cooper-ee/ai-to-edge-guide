# 10 · AI 编译器：计算不变，安排可以不同

> 状态：已展开。目标：理解图优化、张量程序、分块和目标后端。前置：矩阵乘法与第 03、05 课。

## 本课结论

编译器不是简单把 Python 翻译成 C。它需要保留计算语义，改变数据流、循环组织、存储与指令映射，并遵守 shape、dtype 和目标硬件约束。优化先验证正确性，再验证速度。

## 同一个矩阵乘法的两种视角

图层看到 `MatMul -> Bias -> ReLU`，可以分析数据依赖、常量折叠、融合或布局改写。张量程序层看到：

```math
C_{ij}=\sum_{k=0}^{K-1}A_{ik}B_{kj}.
```


它要决定循环顺序、tile 大小、并行映射和中间数据存在哪里。融合能减少中间写回与启动，但可能增加寄存器压力或破坏高效库调用；不是算子越少越快。

大白话：数学表达规定“最终要算出什么”，schedule 规定“工人分哪组、材料先搬哪块、哪个结果留在手边”。工序相同，材料搬运次数可以差很多。

## 分块为什么减少重复搬运

若分别计算一个输出元素，每个元素都需要相应的一行 A 和一列 B。一次算 $`b\times b`$ 的输出块，在一个 K 分块里读入两个 $`b\times b`$ 输入块，做约 $`2b^3`$ 次浮点运算。忽略输出与其他开销、每元素 $`s`$ 字节时，算术强度约为：

```math
I\approx\frac{2b^3}{2b^2s}=\frac b s.
```


tile 越大，潜在复用越多，但缓存/共享内存/寄存器容量有限，过大会溢出或减少并发。这个估计说明方向，不直接给最优 tile。

## 可运行的分块实验

```powershell
python -m edge_ai_labs --lab compiler
```

`math_labs.py::compiler` 构造 $`17\times11`$ 与 $`11\times13`$ 的矩阵，按 tile=4 计算，并对照 NumPy `a @ b`。尺寸特意不整除 tile，检查尾块。这里每块仍调用 NumPy 矩阵乘，Python 循环也有开销，因此不能用它证明 GPU 分块 Kernel 加速。

接着用合成上限 $`P_{peak}=1`$ TFLOP/s、$`BW=20`$ GB/s、$`I=2`$ FLOP/byte 算 Roofline，得到 40 GFLOP/s 的带宽上限；拐点为 50 FLOP/byte。它不是任何具体芯片指标。公式和单位可独立核算。

## TVM 的知识结构

TVM 原始论文讨论端到端优化与代码生成：[Chen 等，2018，OSDI，PDF](https://arxiv.org/pdf/1802.04799)。当前工程学习应同时看官方文档，不能把 2018 年实现当作当前 API。

| 抽象层 | 关注的问题 | 阅读入口 |
|---|---|---|
| 图/Relax | shape 关系、算子组合和数据流 | [Relax](https://tvm.apache.org/docs/deep_dive/relax/index.html) |
| 张量程序/TensorIR | 循环、buffer、访存和调度 | [TensorIR](https://tvm.apache.org/docs/deep_dive/tensor_ir/index.html) |
| Target/CodeGen | 指令、设备能力、外部库 | [TVM 架构](https://tvm.apache.org/docs/arch/index.html) |
| Runtime | 模块加载、调用、设备资源 | [TVM 总文档](https://tvm.apache.org/docs/index.html) |

具体模块名随版本演进；教程不将某个 `tir` 导入路径写成永久事实。BYOC 接入厂商代码生成需要后端实现，不意味着任意 NPU 只改一个 target 名就能使用。

## 优化时必须检查哪些语义

浮点加法不满足精确结合律，改变 reduction 顺序可能改变低位；融合激活可能改变中间舍入；布局改变需要同步更新 stride；动态 shape 需要实际约束；含随机数或状态更新的操作不能任意重排。容差要结合任务与精度选择。

排错按顺序：最小输入参考输出 → 原始图 → 每一优化阶段 IR → 单算子 → 目标设备。先找首个数值偏离的位置，再谈最终输出。暂缓真实 TVM 构建与 autotuning，它们属于有对应硬件和固定编译环境后的扩展任务。

过关任务：解释把 `17` 改成 `16` 后少了哪类边界检查；说明为什么“tile=32 比 tile=16 大”不足以推出更快。

<!-- COURSE-NAV -->

---

[路线总览](roadmap.md) · [课程与源码](../tutorial.md) · [配套练习](../practice.md) · [上一课 09](09-serving-and-runtimes.md) · [下一课 11](11-kernel-and-flashattention.md)
