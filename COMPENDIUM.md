# Invoice Processor – Compendium

## Project Overview

- **Purpose**: Extract key fields from PDF invoices and generate an Excel reimbursement summary.
- **Live URL**: https://web-production-9937.up.railway.app/
- **GitHub**: https://github.com/NinaGXie/invoice-processor
- **Interfaces**:
  - Web UI (`app.py`) — drag-and-drop upload, works locally and on Railway
  - CLI (`invoice_processor.py`) — `python3 invoice_processor.py /path/to/folder`
- **Supported invoice types**: Chinese VAT invoices, train tickets, flight tickets, hotel receipts, taxi/ride-sharing, restaurant receipts, office supplies, shipping, telecom, and generic international invoices.

## Directory Layout

```
Invoice Reader/
├─ app.py                  # Flask web server (port 5001)
├─ invoice_processor.py    # Core extraction logic + CLI entry point
├─ requirements.txt        # Python dependencies
├─ Procfile                # Railway/Heroku: gunicorn app:app
├─ Aptfile                 # System deps for Railway: tesseract, poppler
├─ templates/
│   ├─ index.html          # Upload page (dark theme)
│   └─ success.html        # Download page (dark theme)
├─ static/
│   └─ biosheng_logo_v2.png
└─ *.md                    # Documentation
```

## Key Functions

| Function | Description |
|----------|-------------|
| `extract_text_from_pdf()` | pdfplumber first, OCR fallback via Tesseract |
| `extract_invoice_data()` | Regex extraction of amount, date, destination, route |
| `categorize_invoice()` | Maps keywords to category (火车票, 飞机票, etc.) |
| `extract_month_day()` | Parses date string into integer month/day |
| `create_excel()` | Writes Excel with headers, data, dropdown, 合计 row |

## Excel Output Columns

序号 / 月 / 日 / 报销内容 / 报销金额 / 发票类型 (dropdown) / 事项 (route for train/flight) / 项目名�� / 合计

## Environment

### Local
```bash
conda activate bio
python3 app.py  # http://localhost:5001
```

### Deploy (Railway)
Push to `main` on GitHub — Railway auto-deploys.
```bash
git add .
git commit -m "your message"
git push
```

## UI

- Dark theme (`#030712` background) matching Biosheng internal tool standard
- Header: app title left, `biosheng_logo_v2.png` right, padding `20px 32px`
- See `UI_Layout_Guide.md` → "Flask App UI Reference" for reusable patterns

---
*Updated 2026-03-14*
