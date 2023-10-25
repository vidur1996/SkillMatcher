from PyPDF2 import PdfReader

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    page = reader.pages[0]
    pdf_data = page.extract_text()
    return pdf_data