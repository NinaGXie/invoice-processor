# CLAUDE_NOTEs – Guidance for Claude Code

## Purpose
These notes give Claude Code context on how to work with the Invoice Processor project.

## Repository Structure
```
Invoice Reader/
├─ app.py                  # Flask web server (port 5001)
├─ invoice_processor.py    # Core extraction logic + CLI
├─ requirements.txt        # Python dependencies
├─ Procfile                # gunicorn app:app (Railway)
├─ Aptfile                 # tesseract + poppler (Railway)
├─ templates/
│   ├─ index.html          # Upload page (dark theme)
│   └─ success.html        # Success/download page (dark theme)
├─ static/
│   └─ biosheng_logo_v2.png
└─ *.md                    # Documentation
```

## Key Files & Functions
- **`invoice_processor.py`**
  - `extract_text_from_pdf()` – pdfplumber first, OCR fallback
  - `extract_invoice_data()` – extracts amount, date, destination, route
  - `categorize_invoice()` – maps to 火车票, 飞机票, 住宿, 打车, 餐饮, 办公用品, 快递, 通讯, 其他
  - `extract_month_day()` – returns integer month and day
  - `create_excel()` – writes Excel with dropdown on 发票类型, 合计 row at bottom
- **`app.py`** – Flask on port 5001, calls invoice_processor logic

## Excel Column Order
序号, 月, 日, 报销内容, 报销金额, 发票类型, 事项, 项目名称
- 报销内容 = category (e.g. 火车票)
- 发票类型 = blank with dropdown (纸质普通发票, 纸质专用发票, 电子普通发票, 电子专用发票)
- 事项 = route for train/flight (e.g. 北京南->苏州北), blank otherwise
- 合计 row: label in column A, SUM formula in column E

## Versions
- **Live**: https://web-production-9937.up.railway.app/
- **GitHub**: https://github.com/NinaGXie/invoice-processor
- **Local**: `conda activate bio && python3 app.py` → http://localhost:5001

## Deploying Changes
```bash
git add .
git commit -m "your message"
git push  # Railway auto-deploys
```

## UI Notes
- Dark theme, Biosheng logo (`biosheng_logo_v2.png`) in top-right header
- Logo must be in `static/` folder with ASCII filename
- See `UI_Layout_Guide.md` → "Flask App UI Reference" for reusable patterns

## Performance Notes
- OCR is expensive — only triggered when pdfplumber returns < 50 chars
- PDFs processed sequentially

---
*Updated 2026-03-14*
