# Output Example

After running the skill, the output folder may contain:

```text
outputs/
└── cnki_fulltext_output/
    ├── 1_文献标题.txt
    ├── 2_文献标题.txt
    └── failed_and_skipped_articles.csv
```

## TXT File Format

Each successfully collected TXT file contains metadata and full text:

```text
标题：
作者：
来源：
时间：
============================================================

正文内容……
```

## CSV File Format

The CSV file records skipped or failed articles:

```text
序号,题名,作者,来源,时间,跳过/失败原因
```

Possible reasons include:

```text
跳过：无 HTML 全文
失败：详情页无 HTML 阅读按钮
失败：正文解析为空或加载超时
失败：发生异常
```

## Expected Result

The skill should generate:

1. TXT files for successfully extracted full texts.
2. A CSV file for skipped or failed records.
3. Console logs showing the number of successful, skipped, and failed articles.