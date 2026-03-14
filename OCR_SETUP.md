# Installing OCR Dependencies

To enable OCR for image-based PDFs, you need to install:

## Option 1: Install Homebrew first (Recommended)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install dependencies:
```bash
brew install tesseract tesseract-lang poppler
```

## Option 2: Manual Installation
Download and install from:
- Tesseract: https://github.com/tesseract-ocr/tesseract/wiki
- Poppler: https://poppler.freedesktop.org/

## After Installation
Run the invoice processor again:
```bash
python3 ~/Desktop/invoice_processor.py "/path/to/invoices"
```

The app will automatically use OCR for image-based PDFs.
