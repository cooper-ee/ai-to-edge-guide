# 本次实际验证记录

基础实验验证日期：2026-10-19；数学排版与文档回归日期：2026-10-20。本目录保存实际运行生成的原始数据，不用模拟值替代真实硬件结果。运行范围是 Windows CPU；环境虽然安装了带 CUDA 的 PyTorch wheel，本项目代码没有把张量或模型移到 GPU。

## 环境与依赖

Python 3.10.20；NumPy 2.2.6；PyTorch 2.11.0+cu128；ONNX 1.23.2；ONNX Runtime 1.23.2；ONNXScript 0.7.2；ONNX IR 1.0.0。完整环境见 [report-full.json](report-full.json)。不同平台建议先用 requirements 安装兼容依赖，并保留实际版本，不保证逐位相同。

## 结果与验收边界

| 检查 | 本次结果 | 说明 |
|---|---|---|
| NumPy 逻辑回归 | 测试准确率约 0.9722 | 900条合成样本，非真实业务 |
| 有限差分梯度 | 最大误差约 $`2.70\times10^{-12}`$ | float64，epsilon=$`10^{-5}`$ |
| 缓存 attention | 最大误差约 $`3.33\times10^{-16}`$ | NumPy 数值参考 |
| 分块 online attention | 最大误差约 $`4.44\times10^{-16}`$ | 不代表 GPU Kernel 速度 |
| 合成 KV 配置 | 48 MiB / 混合full层部分12 MiB | 不同于真实 Qwen 配置 |
| 调度模拟 | 静态16 tick、连续12 tick | 没有真实系统开销 |
| 词项检索 | 4题 Recall@2=1 | 小型固定检索题，无LLM生成 |
| PyTorch MLP | 114参数，测试准确率约0.9556 | 验证损失选择checkpoint |
| 动态ONNX | 最大绝对误差 $`9.54\times10^{-7}`$ | batch=1/7/32/64，另对封存数据评价 |
| 微型LM | loss约3.48→0.91，缓存logits误差约 $`3.81\times10^{-6}`$ | 100步玩具语料；非泛化评测 |
| 因果性 | 改未来输入，较早logits最大差0 | 检查未来信息泄漏 |
| 静态ONNX | checker与10组独立输入数值对照通过 | 不代表RKNN转换与NPU通过 |
| 测试 | 16项通过 | 包括HTTP、数值/调度边界和8项数学文档回归 |
| 浏览器 | 桌面1440×1080、手机390×844检查通过 | 交互计算、无JS错误、SVG文本未越界 |
| 离线阅读 | 阻断HTTP/HTTPS后149个公式渲染通过 | 使用本地MathJax SVG组件 |
| GitHub数学解析 | 169个公式均识别，内容逐项一致 | GitHub Markdown API实际响应 |
| GitHub转换结果的本地排版 | 169个公式，0个错误、0个未渲染节点 | API生成HTML在本地MathJax中检查；未发布远程文件 |

具体状态与结果见 [audit.json](audit.json)、[browser-check.json](browser-check.json)、[github-math-check.json](github-math-check.json)、[github-browser-check.json](github-browser-check.json)、[tests.txt](tests.txt)、[docs-check.json](docs-check.json)。

## 原始文件

- [report-full.json](report-full.json)：11个实验、环境、种子与运行时间。
- [training_curve.json](training_curve.json)：MLP逐epoch训练与验证损失。
- [tiny_lm_curve.json](tiny_lm_curve.json)：微型LM训练损失，不含独立泛化评估。
- [benchmark.json](benchmark.json)：单线程CPU预处理+forward的原始毫秒数组。不是HTTP吞吐。
- [file-manifest.json](file-manifest.json)：本次交付文件指纹；不含自身、运行缓存和本地大模型产物。

## 可复现命令

```powershell
python -m edge_ai_labs --lab full --seed 42
python adapters/export_static.py
python scripts/audit_report.py
python -m unittest discover -s tests -v
python scripts/benchmark.py
python scripts/check_docs.py
```

可选UI验证先安装 `requirements-ui.txt`，并准备Chrome/Chromium；执行 `python scripts/qa_browser.py`。可以用 `--browser` 指定现有浏览器路径。

llama.cpp、vLLM、MLC、TVM编译、RKNN、RKLLM和多模态板端工作流均未在此环境实测。相关内容为有明确前置、检查点与失败边界的学习手册/适配模板。
