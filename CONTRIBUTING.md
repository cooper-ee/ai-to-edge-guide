# 如何贡献

欢迎改正推导、补充可复现实验或提交设备结果。优先提交最小、可核查的改动。

1. 说明问题、涉及章节和预期变化。
2. 数学结论给假设、单位、小例子和来源；软件行为给版本/commit。
3. 实验使用 `templates/experiment.md`，附完整命令、环境、种子与原始结果。
4. GPU/NPU 结果附 `templates/version-matrix.md`，不要把未测平台标成通过。
5. 运行基础实验、相关测试和 `python scripts/check_docs.py`。
6. 修改章节标题或文件名时更新 `scripts/build_docs.py` 的课程列表，再生成导航。

公式按 [数学排版规范](docs/math-formatting.md) 编写；离线检查会拒绝容易与 Markdown 冲突的旧定界方式。需要核对 GitHub 解析时，可另运行 `python scripts/check_github_math.py`；该命令仅调用预览接口，不提交仓库文件。

生成文件由对应脚本维护：图示 `build_visuals.py`，源码导航/习题/阅读页 `build_docs.py`。正文在 `docs/` 编辑。不要提交虚拟环境、下载模型、密钥和个人机器路径。

基础 CI 只验证 NumPy 数值与文档；PyTorch/ONNX 改动请在本机运行完整流程并保存报告。纠错时明确原结论错在哪里、修正后哪些实验应变化。
