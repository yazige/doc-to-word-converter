# 质量检查与表格检查

这个项目不把“生成了 Word 文件”当成结束。真正交付前，至少要确认三件事：

1. 文档不是空的；
2. 隐私风险已经清掉；
3. 表格结构能编辑，不是截图或大段文字伪装出来的表格。

## 隐私清理

先清理 Word 元数据：

```bash
python scripts/privacy_scrub_docx.py output.docx output_scrubbed.docx
```

再检查隐私风险：

```bash
python scripts/check_docx_privacy.py output_scrubbed.docx
```

它会检查：

- 长数字串；
- 手机号；
- 邮箱；
- 类似统一社会信用代码的字符串；
- 公司后缀；
- Word 内部媒体文件；
- Word 修订痕迹和 `rsid`。

## 基础质量检查

```bash
python scripts/check_docx_quality.py output_scrubbed.docx
```

它会检查：

- 文档是否有正文；
- 表格是否有足够单元格内容；
- 字体是否出现异常值。

## 表格粒度检查

```bash
python scripts/check_docx_table_granularity.py output_scrubbed.docx --min-rows 8 --max-newlines-per-cell 3
```

这个检查主要防两类问题。

第一类是“表格被压扁”：源表明明有很多行，输出 Word 只有几行，大量内容靠换行塞在一个单元格里。

第二类是“过度拆表”：源表本来有合并单元格，用来表示分组、类别、评分标准或备注块，转换时却全拆成重复文字。

如果源表本来没有合并单元格，或者你明确想要全部独立单元格，可以加：

```bash
--no-merged-cells
```

但不要默认加这个参数。很多业务表单里的合并单元格是有意义的。

## 人工复查重点

脚本检查通过后，还是建议用 Word 打开看一遍：

- 页面方向是否跟原文件一致；
- 表头是否被扁平化；
- 斜线表头是否还在；
- 明细行是否可以逐行编辑；
- 分组列是否按原表合并；
- 有没有整页截图冒充 Word；
- 有没有真实公司名、人员姓名、手机号等残留。

自动检查负责拦底线，人工复查负责判断像不像原表。
