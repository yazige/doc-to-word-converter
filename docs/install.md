# 安装与初始化

## 1. 安装 skill

把这个目录复制到你的 Codex skills 目录：

```text
skills/doc-to-word-converter
```

复制后重启 Codex。重启是为了让 Codex 重新扫描本地 skill。

如果你不确定自己的 skills 目录在哪里，可以先在 Codex 里问：

```text
我的 Codex skills 目录在哪里？请帮我确认 doc-to-word-converter 应该复制到哪里。
```

## 2. 准备转换工作区

建议新建一个单独文件夹，例如：

```text
~/Desktop/转Word
```

里面放三个子文件夹：

```text
TBD
Done
New
```

含义很简单：

| 文件夹 | 用途 |
|---|---|
| `TBD` | 还没有转换的源文件 |
| `Done` | 已经成功转换并通过检查的源文件 |
| `New` | 最终生成的 Word 文件 |

如果你已经安装好依赖，可以运行初始化脚本：

```bash
python scripts/init_workspace.py "/你的/转换工作区"
```

## 3. 放入待转换文件

把 PDF、DOCX、PPT、Excel、CSV、图片或扫描件放进 `TBD`。

不要直接修改原始文件。这个 skill 的默认流程是：只有新 Word 通过检查后，才把原文件移动到 `Done`。

## 4. 第一次运行建议

第一次不要一次放太多文件。建议先放 1 到 3 个典型文件，看看转换效果和检查结果。

可以这样对 Codex 说：

```text
使用 doc-to-word-converter skill 处理这个工作区。
先运行初始化、状态统计和复杂度评估。
这次只处理 1 个最适合测试的文件。
生成 Word 后先做隐私检查、质量检查和表格粒度检查，通过后再移动文件。
```

## 5. 常见依赖

建议安装：

```bash
python3 -m pip install python-docx pypdf Pillow
```

如果你需要处理扫描件或纯图片文字，还需要 OCR：

```bash
python3 -m pip install pytesseract
```

同时还要在系统里安装 Tesseract OCR。没有它时，`pytesseract` 只是 Python 接口，不能真正识别图片。

## 6. 新手注意事项

- 不要把私人合同、客户资料直接开源或发给别人；
- 不要把 API Key、密码、Token 写进转换文件；
- 如果文件包含真实公司名、手机号、邮箱、身份证号，转换后一定要跑隐私检查；
- 如果 Word 打开后表格不好编辑，优先检查是不是“多行内容被塞进一个大单元格”。
