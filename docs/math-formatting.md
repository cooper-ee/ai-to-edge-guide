# 公式写作与维护

本仓库以 GitHub Markdown 与本地离线阅读页为主要阅读入口，统一使用下面的格式。语法依据：[GitHub 官方数学表达式说明](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions)。

## 行内公式

```text
若 $`h=W_1x+b_1`$，$`y=W_2h+b_2`$，则继续代入。
```

公式内的下划线被定界符保护，多条公式紧邻中文标点也不会被识别为普通 Markdown 强调。正文示例：若 $`h=W_1x+b_1`$，$`y=W_2h+b_2`$，则代入后仍为仿射函数。

## 独立公式

下面外层四个反引号只是为了展示内层写法，真实正文只使用内层的 `math` 代码块：

````text
```math
\nabla_w\mathcal L=\frac{2}{n}X^\top(Xw-y).
```
````

矩阵中的双反斜杠表示数学换行，不能转换成普通换行或删掉一根反斜杠。

## 数学名称与代码示例

ReLU、softmax 等名称在公式中使用基础直立字体，例如 $`h=\mathrm{ReLU}(W_1x+b_1)`$。在解释 API 时，仍用普通代码格式，如 `torch.softmax`。

PowerShell 的 `$body` 是代码变量。它应放进普通代码块，不能用全局字符串替换把所有美元符号都当作公式。本仓库的生成器区分数学、普通文本、行内代码和不同长度的围栏代码块。

## 修改后的检查

```powershell
python -m unittest discover -s tests -v
python scripts/build_docs.py
python scripts/check_docs.py
```

需要浏览器检查时，再运行 `scripts/qa_browser.py`。本地渲染通过和 GitHub 在线页面验证是不同检查，报告会分别记录范围。
