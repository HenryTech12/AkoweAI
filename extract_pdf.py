import sys
try:
    import pdfplumber
except ImportError:
    print("Installing pdfplumber...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber"])
    import pdfplumber

pdf_path = r'c:\Users\DELL\Downloads\AkoweAI.pdf'
try:
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                full_text += f"\n--- Page {page_num} ---\n{text}"
        print(full_text)
except Exception as e:
    print(f"Error: {e}")
