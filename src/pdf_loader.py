from PyPDF2 import PdfReader

def load_pdf(pdf_path, source):
    """
    Charge un fichier PDF et extrait son texte page par page tout en construisant une `page_map`
    pour associer chaque position de caractère à un numéro de page.
    """
    pdf_reader = PdfReader(pdf_path)
    text = ""
    page_map = []

    for i, page in enumerate(pdf_reader.pages):
        page_text = page.extract_text()
        if page_text:
            start_idx = len(text)  # Index du début de la page
            text += page_text + "\n"  # Ajout du texte avec un retour à la ligne
            page_map.append((start_idx, i + 1))

    return text, page_map
