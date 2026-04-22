# CLAUDE_NOTEs – Guidance for Claude Code

## Purpose
These notes give Claude Code context on how to work with the Invoice Processor project.

## Repository Structure
```
Invoice Reader/
├─ app.py                  # Flask web server (port 5001)
├─ invoice_processor.py    # Core extraction logic + CLI
├─ requirements.txt        # Python dependencies
├─ Dockerfile              # Docker build with tesseract support
├─ Procfile                # gunicorn app:app (Railway)
├─ nixpacks.toml           # Railway nixpacks config (deprecated, use Dockerfile)
├─ railway.json            # Railway deployment config
├─ Aptfile                 # tesseract + poppler (legacy, use Dockerfile)
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
  - `create_excel()` – writes Excel with dropdown on 发票类型, auto-fills specific categories, 合计 row at bottom
- **`app.py`** – Flask on port 5001, calls invoice_processor logic

## Excel Column Order
序号, 月, 日, 报销内容, 报销金额, 发票类型, 事项, 项目名称
- 报销内容 = category (e.g. 火车票)
- 发票类型 = auto-filled for specific categories:
  - 火车票 → 电子专用发票
  - 飞机票 → 电子专用发票
  - 打车 → 电子普通发票
  - Others → blank with dropdown (纸质普通发票, 纸质专用发票, 电子普通发票, 电子专用发票)
- 事项 = route for train/flight (e.g. 北京南->苏州北), blank otherwise
- 合计 row: label in column A, pre-calculated sum in column E

## Date Extraction Logic
- **Train tickets**: Extracts travel date (e.g., 2026年03月27日 13:00开), NOT invoice issue date (开票日期)
- **Flight tickets**: Extracts travel date from flight itinerary, avoids invoice issue date (填开日期)
- Prioritizes actual travel dates over administrative dates

## Route Extraction Logic
- **Train tickets**: Extracts from format like "北京南 G17 上海"
- **Flight tickets**: Handles OCR multi-line format "A: 上海 浦东 T1 \n :北京 首都 T2"
- Blacklists invalid terms: 燃油, 附加, 保险, 税费, 合计, 金额, 票价

## Versions
- **Live**: https://biosheng-ai-invoice-processor.up.railway.app/ (or current Railway URL)
- **GitHub**: https://github.com/NinaGXie/invoice-processor
- **Local**: `conda activate bio && python3 app.py` → http://localhost:5001

## Deploying Changes
```bash
git add .
git commit -m "your message"
git push  # Railway auto-deploys using Dockerfile
```

## UI Notes
- Dark theme, Biosheng logo (`biosheng_logo_v2.png`) in top-right header
- Logo must be in `static/` folder with ASCII filename
- See `UI_Layout_Guide.md` → "Flask App UI Reference" for reusable patterns

## Performance Notes
- OCR is expensive — only triggered when pdfplumber returns < 50 chars
- PDFs processed sequentially
- Tesseract installed via Dockerfile for Railway deployment

## OCR Notes
- **Local**: Tesseract not required for text-based PDFs (train tickets)
- **Railway**: Tesseract installed via Dockerfile for image-based PDFs (flight tickets)
- OCR quality varies - flight itineraries may have garbled text or missing characters

---
*Updated 2026-04-22*
