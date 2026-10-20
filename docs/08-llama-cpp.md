# 08 · llama.cpp：第一次跑通真实本地语言模型

> 状态：已展开。目标：区分 GGUF、模型权重、会话状态和后端；完成本地推理与基准。前置：第 05–06 课。以下外部工具流程需读者本机执行，本交付未编译实测 llama.cpp。

## 本课结论

llama.cpp 的价值在于把支持的 LLM 架构、量化格式、执行后端和推理工具组织成一个本地系统。GGUF 只是其中的模型容器。能否运行取决于架构、量化类型、运行版本和后端支持的交集。[官方仓库](https://github.com/ggml-org/llama.cpp)

大白话：GGUF 像装好目录和材料的箱子，llama.cpp 是能识别这些材料并按特定结构工作的工坊。箱子后缀相同，不代表里面的每套零件都能被旧版本工坊组装。

## 从源码构建，先固定证据

以下是 Linux/WSL2 的 CPU 路线，要求 Git、CMake 和 C/C++ 工具链。Windows 原生构建使用官方对应指南，二进制目录可能包含 `Release`：

```bash
git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
git rev-parse HEAD > source-commit.txt
cmake -S . -B build -DGGML_CUDA=OFF
cmake --build build --config Release -j 4
./build/bin/llama-cli --help > cli-help.txt
./build/bin/llama-bench --help > bench-help.txt
```

保存 commit 与 `--help` 是为了让后来者知道参数在哪个版本有效。上面不把移动的分支写成固定复现实验版本。正式复现应使用实验报告记录的 commit 重新 checkout。[官方构建文档](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)

从 [Qwen 官方 Qwen2.5-0.5B-Instruct-GGUF 模型页](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF) 的文件列表选取当前工具支持的完整 GGUF 文件，放到 `models/model.gguf`；记录文件名、模型 revision 与 SHA256。选择它是为了先学习成熟的小模型链路，不代表最优质量或固定内存承诺。若文件分片，按模型页和 Runtime 的说明处理，不要随意拼接。

```bash
sha256sum models/model.gguf > model.sha256
./build/bin/llama-cli -m models/model.gguf -p "Explain KV cache briefly." -n 64
./build/bin/llama-bench -m models/model.gguf -p 128 -n 32 -t 4
./build/bin/llama-server -m models/model.gguf --host 127.0.0.1 --port 8080
```

参数以刚保存的帮助为准。先查看日志中的后端、上下文和模板；对话模型应使用匹配的 chat template。`llama-bench` 的 prompt processing / token generation 测量不是 HTTP 服务的完整 TTFT。

## 加载和执行到底分几层

阅读外部源码时，按当前 checkout 搜索行为，避免把随版本变化的行号当永久链接：

```bash
rg "llama_model_load_from_file|llama_init_from_model|llama_decode" examples tools src include
rg "gguf_init_from_file|backend_sched" src ggml
```

主链：工具解析参数 → 读取 GGUF 元数据和张量信息 → 建立模型对象 → 创建上下文/缓存 → 输入 token → 构图与后端执行 → logits → 采样。权重通常跨请求复用，会话 KV 和采样状态则随请求变化。某些源码符号会演进，搜索不到时从当前 public header 和工具入口反向追踪，不照搬旧教程函数名。

## 量化格式不只是 Q4 这两个字符

GGUF 量化可能包含分组、scale、高精度保留和混合类型。Q4_K_M 等名称不能直接解释为“所有参数精确 4 bit”。转换、量化和推理是不同步骤；转换器支持模型结构，不意味着所有量化 Kernel 在你的后端上都高效。

要做可信比较，固定模型、prompt token 数、输出数、线程、上下文、offload 配置和采样参数，再比较文件大小、运行内存、prefill、decode 与任务质量。不要把不同模型或不同量化质量的速度比写成纯 Runtime 优势。

## 排错与过关任务

加载失败先检查文件是否完整、架构支持和版本；输出异常先核对 tokenizer/template，再排查量化；很慢则先检查是否真的走了预期后端与线程。不要因设备带 NPU 就假定 llama.cpp 已使用它。

过关交付：一份记录 commit、模型 SHA256、完整命令、日志和原始计时的报告。没有这些证据时写“待测”。本仓库可先用 `--lab tiny-lm` 练习缓存机制，再用本课的大模型验证工程链路。

<!-- COURSE-NAV -->

---

[路线总览](roadmap.md) · [课程与源码](../tutorial.md) · [配套练习](../practice.md) · [上一课 07](07-rag-and-agent.md) · [下一课 09](09-serving-and-runtimes.md)
