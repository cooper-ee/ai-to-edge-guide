# 11 · GPU Kernel 与 FlashAttention：少搬中间结果

> 状态：已展开。目标：推出在线 softmax，理解 IO 优化与数学复杂度的区别。前置：第 04、10 课。数值实验只需 CPU；没有 GPU 性能实测。

## 本课结论

FlashAttention 的关键不是删掉标准注意力中的两两交互，而是用分块与在线归一化减少大中间矩阵在慢速存储层的读写。算法的数值等价和 GPU 的运行加速要分别验证。[Dao 等，2022，NeurIPS，PDF](https://arxiv.org/pdf/2205.14135)

## 先看朴素注意力的材料流

先算 $S=QK^\top$，再写回；读 $S$ 算 softmax 得到 $P$，再写回；读 $P$ 和 V 求输出。序列长时，$T\times T$ 中间矩阵可能成为重要的容量和流量开销。

大白话：如果一边读一边累计最终答案，就不必把所有中间草稿都搬到仓库再搬回来。关键难点在于 softmax 的分母依赖整行，不能天真地“每块各做 softmax 再拼接”。

## 在线 softmax 从合并两个分块推导

对已经处理的分数集合，保存三个量：最大值 $m$、归一化分母 $\ell$、未归一化加权和 $a$：

$$\ell=\sum_j e^{s_j-m},\qquad a=\sum_j e^{s_j-m}v_j.$$

新块的最大值为 $m_b$，记 $m'=\max(m,m_b)$。把旧结果换到同一指数基准，再加新块：

$$\ell'=e^{m-m'}\ell+\sum_{j\in b}e^{s_j-m'},$$
$$a'=e^{m-m'}a+\sum_{j\in b}e^{s_j-m'}v_j,\qquad o=a'/\ell'.$$

为什么能这样合并？因为 $e^{s_j-m}=e^{s_j-m'}e^{m'-m}$，旧项乘 $e^{m-m'}$ 就与新项处在同一基准。初始化 $m=-\infty,\ell=0,a=0$。最大值移位让指数不容易上溢。

例子：分数 `[1,2]`，value `[10,20]`。先读第一项得到 $m=1,\ell=1,a=10$；第二项使 $m'=2$，更新 $\ell'=e^{-1}+1$，$a'=10e^{-1}+20$；结果约 17.31，与一次性 softmax 完全同义，浮点舍入除外。

## 本仓库真正实现了哪部分

`math_labs.py::online_attention` 对每个 query 逐 key 块更新三个量，支持因果 attention 和不能整除的尾块。它不会构造完整 $T\times T$ scores；但它是 NumPy/Python 数学参考，不是 FlashAttention GPU Kernel 的性能复现。

```powershell
python -m edge_ai_labs --lab attention
python -m unittest discover -s tests -v
```

测试除了普通输入，还包括大幅值 logits、block=1/4/32、尾块与“改未来不能影响过去”的检查。读完 `dense_attention` 后看 `online_attention` 的 `rescale`，思考如果漏乘它，哪个量会先失真。

## 接入 GPU 时还要理解什么

| 概念 | 影响什么 |
|---|---|
| grid/block/thread | 工作如何分配；同步可以发生在哪个范围 |
| 全局内存/共享内存/寄存器 | 容量、访问代价与数据复用 |
| 合并访存 | 相邻线程的数据访问是否适合硬件 |
| Tensor Core/MMA | 支持的 dtype、tile 与矩阵操作 |
| occupancy | 活跃工作数量；过高也不保证最快 |
| launch 与同步 | 小算子时可能占显著比例 |

具体执行语义见 [NVIDIA 官方 CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/index.html)；在受支持 GPU 上继续阅读 [Triton 官方 Fused Attention 教程](https://triton-lang.org/main/getting-started/tutorials/06-fused-attention.html)。不要把 NVIDIA 的线程组织细节套给所有 NPU。

## 三个容易混淆的复杂度

完整 attention 的两两交互算术仍通常为 $O(T^2d)$；避免存储完整中间矩阵能改善额外存储与 IO；单次 decode 的 query 长度是 1，其 shape 和 prefill 不同。谈“线性内存”时必须说明是哪个张量、哪个阶段和哪一项额外空间。

过关任务：反驳“FlashAttention 用近似换速度”和“FlashAttention 让所有 attention FLOPs 变成线性”这两句话，分别指出错误发生在数学语义还是复杂度口径上。硬件编译与 NPU 工程在下一课展开。

<!-- COURSE-NAV -->

---

[路线总览](roadmap.md) · [课程与源码](../tutorial.md) · [配套练习](../practice.md) · [上一课 10](10-compiler.md) · [下一课 12](12-rknn.md)
