# 00 · 先搭一张能用于排错的地图

> 状态：已展开。目标：说清数据、模型、格式、Runtime、编译器和硬件各自负责什么。前置：会运行 Python 文件。

## 本课结论

“训练出了权重”只完成了一段工作。部署还必须把模型的输入约定、计算规则、参数和执行环境拼齐。先做一个小模型的完整交付，比同时安装五个推理框架更容易建立正确认知。

把模型看成菜谱会很直观：结构是做菜步骤，权重是调料配比，输入预处理是备菜，Runtime 是实际组织做菜的厨房，Kernel 是某一道具体工序，编译器负责把步骤安排得适合这个厨房。菜谱能读，不代表厨房里有所有设备；模型文件能加载，也不代表结果正确。

![模型到硬件的分层图](../assets/stack.svg)

## 最少的数学与计算机基础

| 基础 | 必须会到什么程度 | 立即验证 |
|---|---|---|
| 向量与矩阵 | 判断矩阵乘法能否进行 | `[B,K] @ [K,N] -> [B,N]` |
| 导数与链式法则 | 区分局部导数和整体梯度 | 推出平方损失对权重的导数 |
| 概率 | 理解条件概率与负对数似然 | 概率小的真标签为什么损失大 |
| Python | 函数、模块、异常、虚拟环境 | 从仓库根目录运行模块 |
| 内存 | 区分容量、带宽和缓存 | 1 GiB 是 $`2^{30}`$ 字节 |
| Linux | 进程、文件、动态库、权限 | 找到进程日志和所加载的库 |
| Git | 提交、版本、差异 | 用一次提交绑定代码与实验配置 |

以线性层为例：$`X\in\mathbb R^{B\times K}`$，PyTorch 风格权重 $`W\in\mathbb R^{N\times K}`$，$`Y=XW^\top+b`$。参数量为 $`NK+N`$。按一次乘法和一次加法计两次浮点操作，主计算量近似 $`2BKN`$ FLOPs。**参数量不随 batch 增大，计算量会增大**。内存容量决定能否放下；内存带宽决定每秒能搬多少数据；FLOP/s 决定每秒能做多少浮点运算。三者不能互相代替。

## 安装与第一次运行

要求 Python 3.10+。在仓库根目录执行；先只安装 NumPy，不需要 GPU，也不下载模型：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m edge_ai_labs --lab all --seed 42
```

Linux/macOS 的激活命令为 `source .venv/bin/activate`，其余命令相同。若已有可用 PyTorch 环境，也可直接使用其中的 Python。输出的 `artifacts/report-all.json` 应包含 8 个实验的数值和环境版本。随机种子用于减少实验漂移，不保证不同硬件或不同版本逐位相同。[PyTorch 可复现性说明](https://docs.pytorch.org/docs/stable/notes/randomness.html)

需要训练、导出时逐步增加依赖：

```powershell
python -m pip install -r requirements-torch.txt
python -m edge_ai_labs --lab classifier
python -m edge_ai_labs --lab tiny-lm
python -m pip install -r requirements-export.txt
python -m edge_ai_labs --lab export
```

`--lab all` 指基础 8 实验；`--lab full` 运行全部 11 个，包含 PyTorch 与 ONNX。完整运行后执行 `python -m unittest discover -s tests -v`。首次安装 PyTorch 的下载时间与实验运行时间分开记录。

## 一次请求的主链与源码顺序

1. `edge_ai_labs/__main__.py::main`：解析 `--lab`、`--seed` 和输出目录，选择实验。
2. `edge_ai_labs/__main__.py::run`：把实验名映射到函数，依赖不足会抛出导入错误。
3. `edge_ai_labs/math_labs.py` 或 `systems.py`：产生数据并完成计算，返回可序列化指标。
4. `main`：写 JSON 报告。训练模型另写本地权重；默认不会提交到 Git。

如果报 `No module named edge_ai_labs`，先检查当前目录是否含 `edge_ai_labs/`；若报 `No module named onnx`，检查是否用**同一个解释器**执行安装与运行。暂缓看 RKNN、RKLLM，它们由第 12–13 课负责。

## 过关任务

用自己的话串起“输入文件 → 预处理 → 张量 → 算子 → Kernel → 输出”，并举出“ONNX 文件正确但部署结果错误”的两个原因。能独立完成这一解释后，再进入机器学习。

<!-- COURSE-NAV -->

---

[路线总览](roadmap.md) · [课程与源码](../tutorial.md) · [配套练习](../practice.md) · [下一课 01](01-machine-learning.md)
