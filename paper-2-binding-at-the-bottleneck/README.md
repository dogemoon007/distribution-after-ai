# Binding at the Bottleneck — v1.0 发布包

第二篇学术短文，接续《Separating Capture from Allocation》。

## 内容
- `Binding_at_the_Bottleneck_v1.0.pdf` — 英文正本，10 页。
- `把规则卡在瓶颈上_中文译本_v1.0.pdf` — 中文译本，11 页，以英文版为准，不单独投稿。
- `bottleneck.tex`（pdflatex）/ `bottleneck-zh.tex`（xelatex，需 Noto Sans CJK SC）— 单文件源码，正文、图、参考文献都在里面。
- `verify_bottleneck.py` — 16 项公式检验，只需 numpy，约 1 分钟，全部 PASS 才算通过。

## 编译
`latexmk -pdf bottleneck.tex`；`latexmk -xelatex bottleneck-zh.tex`。Overleaf 上传单个 .tex 即可。

## 字数（英文）
正文 2,800 词左右，附录约 370 词，合计约 3,200 词。

## SHA-256
- 英文 PDF：`2c5211163a3814897ca3091e25cfae2be5ac1b2a572bfbd13e0c0a8fe5180339`
- 中文 PDF：`9917f301378893cc78ea8b6617a40c21c3e520ae457bf623fb3ca157c2d86126`
