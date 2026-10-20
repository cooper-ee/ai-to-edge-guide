# 02 · 神经网络：把“学参数”拆成能检查的四步

> 状态：已展开。目标：理解非线性、链式法则和训练循环。前置：第 01 课。

## 本课结论

深度网络仍然是在减少损失，只是把线性变换与非线性组合成更丰富的函数。反向传播负责计算导数；优化器负责利用导数更新参数。两者分工不同。

## 为什么多层线性仍然不够

若 $h=W_1x+b_1$，$y=W_2h+b_2$，则 $y=(W_2W_1)x+(W_2b_1+b_2)$，仍然是线性/仿射函数。加上 $h=\operatorname{ReLU}(W_1x+b_1)$ 后，组合才有分段非线性表达能力。大白话：只叠加几次“按比例放大”，不会自动长出判断复杂边界的能力。

本项目 MLP 是 $4\to16\to2$。参数量：$(4\times16+16)+(16\times2+2)=114$。参数很少，仍足以走完训练、模型选择、导出、服务和基准测试。

## 反向传播不是玄学

先考虑 $\hat y=x^\top w$，$\mathcal L=\frac1n\sum_i(\hat y_i-y_i)^2$：

$$\nabla_w\mathcal L=\frac2nX^\top(Xw-y).$$

这可以看成两步：损失告诉预测“你偏了多少”，线性层再告诉每个权重“你对这个偏差贡献多少”。多层网络只是把这样的局部导数按链式法则相乘、相加。

有限差分提供一个独立检查：

$$\frac{\partial\mathcal L}{\partial w_j}\approx
\frac{\mathcal L(w+\epsilon e_j)-\mathcal L(w-\epsilon e_j)}{2\epsilon}.$$

`gradients` 实验用 float64、$\epsilon=10^{-5}$ 对照解析梯度，误差应在 $10^{-8}$ 以下。$\epsilon$ 太大有截断误差，太小会受浮点抵消影响；不是越小越好。自动求导本身也应借助这样的独立数值检查建立信任。

## 一次训练迭代的因果链

1. 前向：输入和权重得到 logits。
2. 损失：把 logits 与标签对照。
3. `backward()`：把梯度写到参数的 `.grad`。
4. `step()`：优化器更新参数。

每轮前调用 `zero_grad()`，因为 PyTorch 默认会累积梯度。累积可以用于梯度累积训练，但忘记清零通常不是你想要的行为。

```python
optimizer.zero_grad(set_to_none=True)
logits = model(features)
loss = criterion(logits, labels)
loss.backward()
optimizer.step()
```

分类器把原始 logits 交给 `CrossEntropyLoss`；不要先 softmax 再把概率传进去。推理时再 softmax 得到展示用概率。`model.eval()` 改变 Dropout、BatchNorm 等模块的行为，`inference_mode()` 控制自动求导开销；二者不是替代关系。

## CNN、RNN 与 Transformer 怎么接上来

CNN 通过局部连接和权重共享处理局部结构。卷积输出边长：

$$H_{out}=\left\lfloor\frac{H+2p-d(k-1)-1}{s}+1\right\rfloor.$$

输入高 $H$、padding $p$、dilation $d$、kernel $k$、stride $s$，每项都影响输出形状。常见错误是只算了空间尺寸，忘记输出通道数。

RNN 把过去压入递推状态 $h_t=f(h_{t-1},x_t)$；Transformer 则通过注意力读取其他位置的信息。它们都在学习函数，但信息流与并行性不同。不能用“Transformer 没有顺序计算”概括自回归生成，生成新 token 仍然依赖上一步结果。

## 实验与源码阅读

```powershell
python -m edge_ai_labs --lab gradients
python -m edge_ai_labs --lab classifier
```

先看 `math_labs.py::gradients`，逐个坐标比较解析梯度与有限差分；再看 `torch_labs.py::classifier`，输入经标准化进入 `model_class`，Adam 更新参数，验证损失决定保留哪份权重，测试只评价被选中的模型。

若训练损失不降，依次检查标签、维度、学习率、梯度是否存在和参数是否进入优化器。若训练降而验证升，先检查过拟合和数据分布，再考虑扩大模型。暂缓 ONNX，下一课处理模型交付。

过关任务：不用“框架帮我做了”这句话，解释 `backward` 后、`step` 前参数和梯度分别发生了什么。参考 [PyTorch 官方自动求导教程](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html)。

<!-- COURSE-NAV -->

---

[路线总览](roadmap.md) · [课程与源码](../tutorial.md) · [配套练习](../practice.md) · [上一课 01](01-machine-learning.md) · [下一课 03](03-export-and-correctness.md)
