# 14 · Linux 与系统集成：把模型变成可观测服务

> 状态：已展开。目标：完成本地 HTTP 模型服务，并规划板端采集/推理集成。前置：第 02–03 课。

## 本课结论

真实应用不仅调用一次 forward，还需要管理输入、请求、线程、内存、日志和关闭流程。本课提供可运行的 CPU HTTP 服务；板端多模态部分是可逐阶段验收的扩展设计。

## 先运行一个小而完整的服务

```powershell
python -m edge_ai_labs --lab classifier
python -m edge_ai_labs.serve --artifacts artifacts --port 8000
```

另开终端发送请求：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
$body = @{features=@(@(1.0,2.0,3.0,4.0))} | ConvertTo-Json -Depth 4 -Compress
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/predict -ContentType 'application/json' -Body $body
```

Linux/macOS 可用：

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' -d '{"features":[[1,2,3,4]]}'
```

本例使用 Python 标准库 HTTP server，绑定 loopback，适合教学和本地联调；没有生产服务的认证、TLS、进程管理与压测承诺。它不是 LLM completion API，也不冒充流式生成服务。

## 沿真实调用链阅读

1. `serve.py::build_server` 读取权重、均值和标准差，并计算模型 SHA256。
2. `Handler.do_GET` 的 `/health` 返回 ready 和模型标识；未知路径返回 404。
3. `Handler.do_POST` 校验请求路径、body 长度和字段集合。
4. 检查输入必须是有限数值的 `[B,4]`，$`1\le B\le64`$。
5. 标准化 → MLP → softmax → JSON 概率和预测；输入错误返回 400。

测试实际启动临时端口，检查健康、正常预测和错误 shape；它不是只调用内部函数的假集成。服务使用只读推理模型，尚未实现排队容量、生产超时治理和滚动发布。

## 系统基础如何围绕问题学习

| 实际问题 | 学习内容 | 可观察证据 |
|---|---|---|
| 动态库找不到 | ELF、动态链接、搜索路径 | `ldd`、实际运行日志 |
| 越跑越慢 | 线程、锁、队列、温度 | CPU 负载、队列长度、温度/频率 |
| 内存持续增长 | 所有权、缓存、缓冲、泄漏 | RSS/PSS、设备缓冲、请求后曲线 |
| 相机输出不对 | V4L2、像素格式、stride | 原始帧与处理后图像 |
| 程序无法停止 | 信号、阻塞 IO、取消与回收 | shutdown 日志与资源释放 |

在 Linux 上先保存只读状态：

```bash
uname -a
cat /etc/os-release
free -h
ps -eo pid,comm,rss,nlwp
```

更深诊断用实际 pid 检查 `/proc/<pid>/smaps_rollup`、打开文件与线程。不要把 `VmSize` 当成物理占用，也不要不区分共享内存就累加多个进程 RSS。

## 多模态扩展：先明确数据流和背压

摄像头采集 → 有界帧队列 → 视觉预处理 → encoder/RKNN → 结果/embedding → 语言侧解释 → 客户端。显示与推理可以使用不同支路。交互场景下可采用“保留最新帧、丢弃过期帧”，而离线录像分析可能要求逐帧处理；策略取决于任务，不能一概丢帧。

记录 capture、enqueue、inference start/end、response 时间，才能区分模型慢还是积压。若输入平均速率超过处理能力，单纯增加队列只会扩大延迟，必须减少输入速率、扩容或明确丢弃/降级策略。

用 C++/Qt 扩展时，将模型资源放入 RAII 对象；工作线程和 UI 线程通过明确消息交接；回调指向的缓冲不能在 UI 使用前释放。先实现静态输入与单次结果，再加实时采集、流式文本和取消。具体 SDK 的线程安全必须按官方契约验证。

过关任务：从原始 HTTP body 复述到最终概率的每一步，说明错误字段为什么返回 400；再设计一个相机 30 FPS、推理 5 FPS 的有界队列策略，并指出你牺牲的是完整性还是时效性。

<!-- COURSE-NAV -->

---

[路线总览](roadmap.md) · [课程与源码](../tutorial.md) · [配套练习](../practice.md) · [上一课 13](13-rkllm.md) · [下一课 15](15-benchmark-and-debug.md)
