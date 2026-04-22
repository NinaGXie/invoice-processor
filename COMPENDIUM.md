# Invoice Processor – Compendium

## Project Overview

- **Purpose**: Extract key fields from PDF invoices and generate an Excel reimbursement summary.
- **Live URL**: https://biosheng-ai-invoice-processor.up.railway.app/
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
├─ Dockerfile              # Docker build with tesseract OCR support
├─ Procfile                # Railway: gunicorn app:app
├─ nixpacks.toml           # Railway nixpacks config (deprecated)
├─ railway.json            # Railway deployment config
├─ Aptfile                 # System deps (legacy, use Dockerfile)
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
| `create_excel()` | Writes Excel with headers, data, dropdown, auto-fill, 合计 row |

## Excel Output Columns

序号 / 月 / 日 / 报销内容 / 报销金额 / 发票类型 (auto-filled or dropdown) / 事项 (route for train/flight) / 项目名称 / 合计

### Auto-filled Invoice Types
- **火车票** → 电子专用发票
- **飞机票** → 电子专用发票
- **打车** → 电子普通发票
- **Others** → Blank with dropdown

## Date Extraction Logic

- **Train tickets**: Extracts travel date (e.g., 2026年03月27日 13:00开), NOT invoice issue date (开票日期)
- **Flight tickets**: Extracts flight date, avoids invoice issue date (填开日期)
- Uses regex patterns with priority ordering to match correct dates

## Route Extraction Logic

- **Train tickets**: Pattern "北京南 G17 上海" → extracts "北京南->上海"
- **Flight tickets**: Handles OCR multi-line format "A: 上海 浦东 T1 \n :北京 首都 T2" → extracts "上海浦东->北京首都"
- Blacklists invalid terms: 燃油, 附加, 保险, 税费, 合计, 金额, 票价

## Environment

### Local
```bash
conda activate bio
python3 app.py  # http://localhost:5001
```

### Deploy (Railway)
Push to `main` on GitHub — Railway auto-deploys using Dockerfile.
```bash
git add .
git commit -m "your message"
git push
```

## UI

- Dark theme (`#030712` background) matching Biosheng internal tool standard
- Header: app title left, `biosheng_logo_v2.png` right, padding `20px 32px`
- See `UI_Layout_Guide.md` → "Flask App UI Reference" for reusable patterns

## OCR Notes

- **Railway**: Tesseract installed via Dockerfile for image-based PDFs
- **Local**: Tesseract optional (only needed for image-based PDFs like flight tickets)
- OCR quality varies - flight itineraries may have garbled text or missing characters
- Debug logging available for troubleshooting OCR extraction

---
*Updated 2026-04-22*
