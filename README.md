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

## Date Extraction

- **Train tickets**: Extracts actual travel date, not invoice issue date
- **Flight tickets**: Extracts flight date, avoids invoice issue date (填开日期)

## Supported Invoice Types

- 火车票 / 飞机票 (with auto route extraction)
- 住宿, 打车, 餐饮, 办公用品, 快递, 通讯, 其他

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
