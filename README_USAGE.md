# Invoice Processor - 发票处理器

A tool to extract invoice data from PDF files and generate Excel reimbursement summaries.

## Live Version

https://web-production-9937.up.railway.app/ — no installation needed.

## Local Version

```bash
conda activate bio
python3 app.py  # opens at http://localhost:5001
```

## Features

- Extract amount, date, and merchant from PDF invoices
- Support for text-based and image-based PDFs (OCR fallback)
- Auto-categorization: 火车票, 飞机票, 住宿, 打车, 餐饮, 办公用品, 快递, 通讯, 其他
- Auto route extraction for train/flight tickets (e.g. 北京南->苏州北)
- Excel output with dropdown for 发票类型 and auto 合计 row
- Dark-themed web UI with Biosheng branding

## Installation (local only)

```bash
pip3 install -r requirements.txt
brew install tesseract tesseract-lang  # for OCR
```

## CLI Usage

```bash
python3 invoice_processor.py /path/to/invoice/folder
```

## Excel Output

| Column | Content |
|--------|---------|
| 序号 | Row number |
| 月 | Month (integer) |
| 日 | Day (integer) |
| 报销内容 | Category (火车票, 飞机票, etc.) |
| 报销金额 | Amount (number) |
| 发票类型 | Blank with dropdown (纸质普通/专用, 电子普通/专用) |
| 事项 | Route for train/flight (e.g. 北京南->苏州北), blank otherwise |
| 项目名称 | Fill manually |
| 合计 | Auto sum of 报销金额 |

## Notes

- Web interface runs on port 5001 locally
- Max file size: 50MB per file
- Multiple file upload supported
