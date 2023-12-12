from PyPDF2 import PdfReader

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    pdf_data = ""
    for i in range (len(reader.pages)):
        page = reader.pages[i]
        pdf_data = pdf_data + page.extract_text()
    return pdf_data