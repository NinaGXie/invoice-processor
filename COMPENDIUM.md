# Invoice Processor

A web-based tool to extract data from PDF invoices and generate Excel reimbursement summaries.

## Live Version

https://biosheng-ai-invoice-processor.up.railway.app/

No installation needed — just open the URL and upload invoices.

## Local Version

```bash
conda activate bio
python3 app.py
```

Then open `http://localhost:5001`.

## Usage

1. Drag and drop PDF invoices onto the upload area
2. Click "处理发票并生成Excel"
3. The Excel file downloads automatically

## Excel Output Columns

| Column | Description |
|--------|-------------|
| 序号 | Row number |
| 月 | Month (number) |
| 日 | Day (number) |
| 报销内容 | Invoice category (e.g. 火车票, 飞机票, 打车) |
| 报销金额 | Amount |
| 发票类型 | Auto-filled for train/flight/taxi, dropdown for others |
| 事项 | Route for train/flight tickets (e.g. 北京南->苏州北) |
| 项目名称 | Fill manually |
| 合计 | Pre-calculated sum of all amounts |

## Auto-filled Invoice Types

- **火车票** (Train) → 电子专用发票
- **飞机票** (Flight) → 电子专用发票
- **打车** (Taxi) → 电子普通发票
- **Others** → Blank with dropdown (纸质普通发票, 纸质专用发票, 电子普通发票, 电子专用发票)

## Supported Invoice Types

- 火车票 / 飞机票 (with auto route extraction)
- 住宿, 打车, 餐饮, 办公用品, 快递, 通讯, 其他

## Date Extraction Logic

- **Train tickets**: Extracts travel date (e.g., 2026年03月27日 13:00开), NOT invoice issue date (开票日期)
- **Flight tickets**: Extracts flight date, avoids invoice issue date (填开日期)
- Uses regex patterns with priority ordering to match correct dates

## Route Extraction Logic

- **Train tickets**: Pattern "北京南 G17 上海" → extracts "北京南->上海"
- **Flight tickets**: Handles OCR multi-line format "A: 上海 浦东 T1 \n :北京 首都 T2" → extracts "上海浦东->北京首都"
- Blacklists invalid terms: 燃油, 附加, 保险, 税费, 合计, 金额, 票价

## Dependencies (local only)

```bash
pip install -r requirements.txt
# OCR not required for text-based PDFs (train tickets)
# For image-based PDFs (flight tickets), tesseract is needed:
brew install tesseract tesseract-lang
```

## Deployment

Hosted on Railway, auto-deploys on every push to `main` on GitHub (NinaGXie/invoice-processor).

```bash
git add .
git commit -m "your message"
git push
```

Railway uses Dockerfile to install tesseract for OCR support.

---

## Technical Details

### Project Structure

```
Invoice Reader/
├─ app.py                  # Flask web server (port 5001)
├─ invoice_processor.py    # Core extraction logic + CLI entry point
├─ requirements.txt        # Python dependencies
├─ Dockerfile              # Docker build with tesseract OCR support
├─ Procfile                # Railway: gunicorn app:app
├─ templates/
│   ├─ index.html          # Upload page (dark theme)
│   └─ success.html        # Download page (dark theme)
├─ static/
│   └─ biosheng_logo_v2.png
└─ COMPENDIUM.md           # This file
```

### Key Functions

| Function | Description |
|----------|-------------|
| `extract_text_from_pdf()` | pdfplumber first, OCR fallback via Tesseract |
| `extract_invoice_data()` | Regex extraction of amount, date, destination, route |
| `categorize_invoice()` | Maps keywords to category (火车票, 飞机票, etc.) |
| `extract_month_day()` | Parses date string into integer month/day |
| `create_excel()` | Writes Excel with headers, data, dropdown, auto-fill, 合计 row |

### CLI Usage

```bash
python3 invoice_processor.py /path/to/folder
```

### UI Design

- Dark theme (`#030712` background) matching Biosheng internal tool standard
- Header: app title left, `biosheng_logo_v2.png` right, padding `20px 32px`

### OCR Notes

- **Railway**: Tesseract installed via Dockerfile for image-based PDFs
- **Local**: Tesseract optional (only needed for image-based PDFs like flight tickets)
- OCR quality varies - flight itineraries may have garbled text or missing characters

---

**GitHub**: https://github.com/NinaGXie/invoice-processor

*Updated 2026-04-22*
