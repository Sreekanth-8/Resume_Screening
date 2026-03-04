from pdfminer.high_level import extract_text
import docx


def extract_text_from_pdf(path):
    try:
        text = extract_text(path)
        if not text:
            return ""
        return text
    except Exception as e:
        print("PDF extraction error:", e)
        return ""


def extract_text_from_docx(path):
    try:
        doc = docx.Document(path)
        full_text = []

        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text.strip())

        return "\n".join(full_text)
    except Exception as e:
        print("DOCX extraction error:", e)
        return ""