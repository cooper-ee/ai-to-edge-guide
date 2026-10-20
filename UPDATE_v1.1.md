# 更新到 v1.1

本次修复公式兼容性并统一项目介绍。更新已有仓库时，无需重新建仓库。

1. 解压 v1.1 完整包，进入 `ai-to-edge-guide` 文件夹。
2. 上传内部文件到已有仓库根目录，覆盖同名文件。也可使用 Git 在本地复制后提交。
3. 删除以下不再使用的旧文件；仅上传同名文件不会自动删除它们：

```text
docs/source-review.md
references/source-snapshot.json
references/original-project-LICENSE.txt
```

第三方声明已整理到 `licenses/THIRD_PARTY_NOTICES.txt`，该文件应随更新包一起上传。

优先核对 `docs/02-neural-networks.md` 的多层线性、ReLU 与参数量公式，再查看第 04–07 课、公式速查表及 `reader.html`。这些页面已同步使用新的数学格式。

如使用网页分批上传，先上传 `docs/`、`references/`、`licenses/`；再上传其余目录和根目录文件。GitHub Pages 更新后可刷新阅读页检查。
