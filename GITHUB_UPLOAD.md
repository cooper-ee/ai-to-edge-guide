# 上传 GitHub 与使用

建议仓库名：`ai-to-edge-learning-lab`。建议描述：**从 AI 基础到端侧部署的中文学习路线：公式直觉、可复现实验、原创动图与部署验证。**

## 用网页上传

1. 解压交付 ZIP，进入 `ai-to-edge-learning-lab` 文件夹。
2. 在 GitHub 新建仓库，使用 Add file → Upload files 上传**这个文件夹内部的文件和目录**。
3. 仓库根目录应直接看到 `README.md`、`docs/`、`edge_ai_labs/`、`index.html`，不要再套一层同名文件夹，也不要只上传 ZIP。
4. 保留 `.github/`、`.gitignore`、`LICENSE`、`references/` 和 `vendor/`；它们分别关系到检查、产物排除和第三方许可。
5. 如想展示交互页面，可在仓库 Settings → Pages 选择分支根目录，参照 [GitHub 官方发布源说明](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。也可以只在本地打开 `index.html`。

## 用 Git 上传

在已解压项目根目录执行，远程URL填你新建仓库的实际地址：

```powershell
git init
git add .
git commit -m "Add AI-to-edge learning lab"
git branch -M main
```

然后按 GitHub 新仓库页面显示的命令添加远程并 push。若要合入已有仓库，先保存已有修改，复制本项目文件后检查差异，避免覆盖已有同名文件。

## 第一次阅读

- GitHub：从 README 的学习路线进入Markdown章节，公式和Mermaid可直接阅读。
- 本地：双击 `index.html` 进入交互实验台；`reader.html` 是含离线公式的完整阅读页。
- 实验：先跑 NumPy 的 `--lab all`；再逐步安装训练/导出依赖。
- 公开展示：使用真实的 `reports/` 结果，硬件待验证状态保留；按自己的实验持续更新。

交付包不含 `.venv`、下载模型、checkpoint或本机缓存；这些由读者按教程生成。不要删除原项目来源与第三方许可说明。
