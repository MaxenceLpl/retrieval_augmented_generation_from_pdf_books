from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

def split_text_into_documents(text, source, page_map, chunk_size=500, chunk_overlap=50):
    """
    Découpe le texte en chunks et associe à chaque chunk les numéros de page correspondants.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    texts = splitter.split_text(text)
    documents = []

    for i, chunk in enumerate(texts):
        # Déterminer la plage de caractères du chunk dans le texte complet
        start_char = text.find(chunk[:20])  # Début du chunk dans le texte original
        end_char = start_char + len(chunk)

        # Trouver les pages associées
        page_start = next((p for c, p in page_map if c >= start_char), "?")
        page_end = next((p for c, p in reversed(page_map) if c <= end_char), page_start)

        metadata = {
            "source": source,
            "page_start": page_start,
            "page_end": page_end
        }
        documents.append(Document(page_content=chunk, metadata=metadata))

    return documents
