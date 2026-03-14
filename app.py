#!/usr/bin/env python3
"""
Invoice Processor Web Application
"""

import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import invoice_processor

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        flash('No files selected')
        return redirect(url_for('index'))

    files = request.files.getlist('files[]')

    if not files or files[0].filename == '':
        flash('No files selected')
        return redirect(url_for('index'))

    # Create temporary directory for this upload
    upload_dir = tempfile.mkdtemp()
    uploaded_files = []

    for idx, file in enumerate(files):
        if file and allowed_file(file.filename):
            # Keep original filename but add index to prevent overwrites
            original_name = file.filename
            name_parts = original_name.rsplit('.', 1)
            if len(name_parts) == 2:
                filename = f"{name_parts[0]}_{idx}.{name_parts[1]}"
            else:
                filename = f"{original_name}_{idx}"

            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            uploaded_files.append(filename)

    if not uploaded_files:
        flash('No valid PDF files uploaded')
        return redirect(url_for('index'))

    # Process invoices
    try:
        pdf_files = list(Path(upload_dir).glob("*.pdf"))
        invoice_data = []

        for pdf_file in pdf_files:
            text = invoice_processor.extract_text_from_pdf(pdf_file)
            data = invoice_processor.extract_invoice_data(text, pdf_file.name)
            invoice_data.append(data)

        # Create Excel file
        output_filename = f"invoice_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = os.path.join(upload_dir, output_filename)
        invoice_processor.create_excel(invoice_data, output_path)

        # Store file path in session or temp location for download
        # For simplicity, we'll use a global dict (in production, use proper session management)
        if not hasattr(app, 'temp_files'):
            app.temp_files = {}

        file_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        app.temp_files[file_id] = output_path

        # Redirect to success page with download link
        return render_template('success.html',
                             file_id=file_id,
                             filename=output_filename,
                             count=len(pdf_files))

    except Exception as e:
        flash(f'Error processing invoices: {str(e)}')
        return redirect(url_for('index'))


@app.route('/download/<file_id>')
def download_file(file_id):
    if hasattr(app, 'temp_files') and file_id in app.temp_files:
        filepath = app.temp_files[file_id]
        filename = os.path.basename(filepath)
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        flash('File not found or expired')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
