import PyPDF2
import docx
import io

def extract_pages_from_pdf(uploaded_file):
    """Yields (page_number, text) for each page in a PDF."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
        for i, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            if text:
                # Yield page number (starting from 1) and its text
                yield i + 1, text
    except Exception as e:
        print(f"Error extracting PDF pages: {e}")
        return

def extract_text_from_file(uploaded_file):
    """Extracts the full text from DOCX or TXT files."""
    file_name = uploaded_file.name
    try:
        if file_name.endswith('.docx'):
            doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
            return "\n".join([para.text for para in doc.paragraphs])
        elif file_name.endswith('.txt'):
            return uploaded_file.getvalue().decode("utf-8")
        else:
            return None
    except Exception as e:
        print(f"Error extracting text from {file_name}: {e}")
        return None