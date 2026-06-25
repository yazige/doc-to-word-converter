# Doc To Word Converter

把 PDF、图片型 Word、扫描件、表单、制度文件转成可编辑 Word 模板的 Codex skill。

很多人说“转 Word”，其实要的不是一个 `.docx` 文件名，而是打开后真的能改、能复用、能交给同事继续填的文档。尤其是制度表、评价表、费用标准表这类文件，最容易出问题：文字能识别出来，但表格被压扁；原表有合并单元格，转换后全拆开；原表是斜线表头，输出里只剩一行普通字段。

这个 skill 就是为这类场景做的。它不是追求一键批量跑完，而是尽量把文档还原成“可编辑、可复查、隐私安全”的 Word 模板。

## 适合谁

- 经常把 PDF、截图、扫描件整理成 Word 模板的人；
- 做行政制度、流程文件、合同模板、评价表、培训表单的人；
- 做跨境电商、项目管理、培训交付，需要把旧资料整理成可复用模板的人；
- 有一堆文件要转 Word，但不想每次都手工调表格、改页边距、删隐私信息的人；
- 想用 Codex 自动化定期处理 `TBD` 文件夹的人。

如果你只是想把纯文字 PDF 粗略导成 Word，普通转换工具可能就够了。这个项目更适合那些“自动转完还要人工修半天”的文档。

## 它解决什么问题

`doc-to-word-converter` 重点处理四件事：

1. **版式不能乱猜**
   - 先检测原文件是横版还是竖版；
   - 输出 Word 必须跟随原文档方向；
   - 检测失败时才保守使用竖版，并明确报告。

2. **表格不能只像表格**
   - 普通表格要变成可编辑 Word 表格；
   - 评价表、打分表、清单表要保留一行一项；
   - 原表有分组合并时，要保留有意义的合并；
   - 原表有斜线表头、多级表头、分组表头时，不能随便扁平化。

3. **隐私信息不能带出去**
   - 公司名、人员姓名、手机号、邮箱、长数字串等要检查；
   - Word 元数据、修订痕迹、`rsid` 等要清理；
   - 不能把整页截图塞进 Word 里假装完成。

4. **批处理不能牺牲质量**
   - 先评估文件复杂度，再决定一次处理几个；
   - 复杂文件单独处理；
   - 每完成一个文件都跑隐私检查和质量检查；
   - 通过后才把原文件移动到 `Done`，把 Word 放进 `New`。

## 最近做过的关键优化

这个 skill 是从真实转换任务里一点点改出来的，最近重点修了这些问题：

### 1. 图片型评价表不能压成大单元格

一张“合伙人资格评价表”原本有 20 多行评价项。早期转换时，表格看起来有列，但实际只有几行，很多评价项被塞进一个大单元格里。打开 Word 后很难编辑。

现在的规则是：评价项、检查项、评分项必须按源表的可见行重建。每条明细仍然是一行。

### 2. 也不能矫枉过正，把所有合并都拆掉

后来又发现另一个问题：原表里本来就有合并单元格，比如“评价维度”“评价子项”“评估结果”“评语备注”这些是分组块。如果全部拆开，虽然每个单元格都独立了，但反而不像原表。

现在的规则改成：

- 明细行保持独立；
- 分组标签按源表保留纵向合并；
- 不做无意义合并，也不强行取消源表有意义的合并。

### 3. 复杂表头要按原结构重建

费用标准表里常见斜线表头、多级表头和分组表头。早期版本会把它们简化成“字段名一行”，信息没丢，但结构已经变了。

现在会尽量保留：

- 斜线表头；
- 两级表头；
- “住宿费 / 交通费 / 出差补助”这类分组表头；
- 表头里的合并关系。

### 4. 增加表格粒度检查

项目新增了 `check_docx_table_granularity.py`。它会检查：

- 表格是否至少有合理行数；
- 单元格里是否塞了过多换行；
- 是否需要禁止合并单元格；
- 是否保留了表格的基本可编辑结构。

这类检查不能替代人工看版式，但能拦住很多“看起来像 Word，实际不好用”的输出。

## 项目结构

```text
.
├── README.md
├── LICENSE
├── docs
│   ├── automation.md
│   ├── history.md
│   ├── install.md
│   └── quality-checks.md
└── skills
    └── doc-to-word-converter
        ├── SKILL.md
        ├── agents
        │   └── openai.yaml
        ├── references
        │   ├── docx-layout.md
        │   └── redaction-rules.md
        ├── scripts
        │   ├── assess_batch_complexity.py
        │   ├── check_docx_privacy.py
        │   ├── check_docx_quality.py
        │   ├── check_docx_table_granularity.py
        │   ├── extract_pdf_images.py
        │   ├── init_workspace.py
        │   ├── pdf_inventory.py
        │   ├── privacy_scrub_docx.py
        │   ├── status_report.py
        │   └── template_text_to_docx.py
        └── tests
            └── test_codex_adaptation.py
```

## 快速开始

1. 把 `skills/doc-to-word-converter` 复制到你的 Codex skills 目录。
2. 重启 Codex，让它重新读取 skill。
3. 准备一个转换工作区，里面放三个文件夹：

```text
TBD   待转换文件
Done  已处理原文件
New   生成后的 Word
```

4. 对 Codex 说：

```text
使用 doc-to-word-converter skill 处理当前工作区的 TBD 文件夹。
先初始化并检查 TBD、Done、New 文件夹，然后运行状态统计和复杂度评估。
质量第一：复杂或不确定文件单独处理。
转出的 Word 横版或竖版必须根据原文档结构检测决定，不能默认横版。
每完成一个文件后运行隐私检查和质量检查；通过后把原文件移动到 Done，把生成的 Word 放到 New。
```

更详细的说明见：

- [安装与初始化](docs/install.md)
- [Codex 自动化设置](docs/automation.md)
- [质量检查与表格检查](docs/quality-checks.md)
- [这个 skill 是怎么改出来的](docs/history.md)

## 依赖说明

基础处理通常需要：

- Python 3
- `python-docx`
- `pypdf`
- `Pillow`

可选能力：

- `PyMuPDF`：更好地读取 PDF 页面尺寸、图片和版式；
- `pytesseract` + Tesseract OCR：处理扫描件和图片文字。

如果没有 OCR 依赖，skill 仍然可以处理有文本层的 PDF、普通 DOCX、Excel/CSV 和部分可人工识别的图片型表单。但它不会假装自己做了 OCR。

## 许可证

MIT License。你可以自由复制、修改、二次分发，也可以按自己的行业改检查规则和表格还原策略。
