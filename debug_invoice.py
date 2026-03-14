#!/usr/bin/env python3
"""Debug script to see what text is extracted from PDFs"""

import sys
import pdfplumber

if len(sys.argv) < 2:
    print("Usage: python3 debug_invoice.py <pdf_file>")
    sys.exit(1)

pdf_path = sys.argv[1]

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Number of pages: {len(pdf.pages)}")
        print("\n" + "="*60)
        print("EXTRACTED TEXT:")
        print("="*60 + "\n")

        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            print(f"--- Page {i+1} ---")
            print(text)
            print("\n")
except Exception as e:
    print(f"Error: {e}")
