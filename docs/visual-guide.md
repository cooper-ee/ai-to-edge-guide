# 图示、动图与论文对照阅读

本项目图示全部为原创教学重绘，不是从论文裁剪后改署名。SVG 可编辑、GIF 可直接在 GitHub 展示，生成代码在 `scripts/build_visuals.py`。

| 图 | 用途 | 对应验证 |
|---|---|---|
| `cover.svg` / `roadmap.svg` | 项目入口与能力路线 | 跳转课程与里程碑 |
| `stack.svg` | 应用到硬件的角色分层 | 一次请求全链复述 |
| `deployment.svg` | 六道正确性检查 | ONNX/ORT 对照与 HTTP 测试 |
| `host-board.svg` | 转换与运行环境分离 | 版本与 artifact hash |
| `roofline.svg` | 计算/带宽上限的直觉 | 仅示意，没有测量数据点 |
| `online-softmax.svg` | 三状态合并逻辑 | 分块与完整 attention 数值对照 |
| `attention.gif` | 因果可见性 | 不是注意力概率，也不是解释归因 |
| `kv-cache.gif` | 追加与复用历史状态 | 图为机制示意，不按真实字节绘制 |
| `batching.gif` | 静态与连续调度 | 抽象 tick，不是硬件耗时 |
| `online-softmax.gif` | 随分数到达更新归一化 | 与第 11 课公式一致 |

## 推荐打开原论文的这些图

- Vaswani 等，2017，[Attention Is All You Need](https://arxiv.org/pdf/1706.03762)：Figure 1 看 encoder/decoder 总体结构，Figure 2 看 scaled dot-product 与 multi-head。现代 decoder-only 模型应另对具体实现核查。
- Dao 等，2022，[FlashAttention](https://arxiv.org/pdf/2205.14135)：Figure 1 结合算法段落看 HBM/SRAM 分层与 IO-aware 思路；不要仅看加速柱状图。
- Kwon 等，2023，[PagedAttention](https://arxiv.org/pdf/2309.06180)：查标题为 PagedAttention 的结构示意，比较逻辑 token 块与物理块。不同版本图号可能变化，按标题定位。
- Williams 等，[Roofline 作者技术报告](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2008/EECS-2008-134.pdf)：看坐标与拐点，再回到本文单位推导。

提供论文链接不代表其全部图片随本项目 MIT 发布。需要在自己的展示中直接转载时，核对该图的许可和署名要求；本仓库直接使用的是自己绘制的教学图。

## 重新生成与阅读方式

```powershell
python -m pip install -r requirements-visuals.txt
python scripts/build_visuals.py
```

脚本会寻找 Windows 微软雅黑、Linux Noto Sans CJK 或 macOS PingFang 字体。缺少中文字体时会明确报错，安装字体后重试。只阅读已有 SVG/GIF 不需要 Python 或字体安装。

`index.html` 的交互不依赖网络，可直接双击。`reader.html` 汇集正文，包含本地 MathJax SVG 公式排版组件，正文与公式均可离线阅读。组件保留独立的 Apache-2.0 许可；见 `vendor/mathjax/NOTICE.md`。GitHub 中应优先用 Markdown 章节，GitHub 会排版数学公式和 Mermaid。
