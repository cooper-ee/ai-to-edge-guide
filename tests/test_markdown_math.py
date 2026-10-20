import unittest
from scripts.markdown_math import parts,normalize,for_html,audit,compatible_tex


class MarkdownMath(unittest.TestCase):
    def test_adjacent_inline_formulae_remain_separate(self):
        original='若 $h=W_1x+b_1$，$y=W_2h+b_2$，则 $y=W_2W_1x$。'
        result=normalize(original)
        self.assertEqual(result,'若 $`h=W_1x+b_1`$，$`y=W_2h+b_2`$，则 $`y=W_2W_1x`$。')
        self.assertEqual(audit(result)['inline'],3)

    def test_shell_code_and_inline_code_are_unchanged(self):
        original='```powershell\n$body = "x"\nWrite-Output $body\n```\n\n`$name` 与 $x_i$。'
        result=normalize(original)
        self.assertIn('```powershell\n$body = "x"\nWrite-Output $body\n```',result)
        self.assertIn('`$name` 与 $`x_i`$。',result)
        self.assertFalse(audit(result)['errors'])

    def test_display_matrix_retains_row_separators(self):
        tex=r'M=\begin{bmatrix}0&1\\2&3\end{bmatrix}'
        result=normalize('前文\n\n$$'+tex+'$$\n\n后文')
        self.assertIn('```math\n'+tex+'\n```',result)
        self.assertEqual([p.tex for p in parts(result) if p.kind=='display'],[tex])

    def test_normalization_is_idempotent(self):
        original='公式 $`x_i`$\n\n```math\ny=x_i^2\n```\n\n代码 `x_i`。'
        once=normalize(original)
        self.assertEqual(once,normalize(once))

    def test_supported_macro_replacement_and_fraction(self):
        self.assertEqual(compatible_tex(r'h=\operatorname{ReLU}(x)+\frac1n'),r'h=\mathrm{ReLU}(x)+\frac{1}{n}')

    def test_comparison_symbols_do_not_pass_through_html(self):
        self.assertEqual(compatible_tex('x_{<t},N>1'),r'x_{\lt t},N\gt 1')
        self.assertFalse(audit(normalize('$N>1$'))['errors'])

    def test_html_conversion_separates_math_from_code(self):
        md,replacements=for_html('`$name` 与 $`x_i`$\n\n```math\ny=x_i\n```\n')
        self.assertIn('`$name`',md)
        self.assertEqual(len(replacements),2)
        self.assertIn(r'\(x_i\)',replacements[0][1])
        self.assertIn(r'\[y=x_i\]',replacements[1][1])

    def test_audit_detects_legacy_and_unbalanced(self):
        self.assertTrue(audit('$x_i$')['errors'])
        self.assertTrue(audit('$`x_{i`$')['errors'])
        self.assertFalse(audit('$`x_i`$')['errors'])


if __name__=='__main__':unittest.main()
