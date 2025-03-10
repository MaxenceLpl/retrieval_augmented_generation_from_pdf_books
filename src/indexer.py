import os
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

class MultiIndex:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialise le gestionnaire d'index multi-livres.
        """
        self.embedding_model = HuggingFaceEmbeddings(model_name=model_name)
        self.indexes = {}

    def build_indexes(self, documents):
        """
        Construit un index FAISS séparé pour chaque livre en conservant les numéros de pages.
        """
        book_groups = {}
        for doc in documents:
            book = doc.metadata.get("source", "Unknown")
            if book not in book_groups:
                book_groups[book] = []
            book_groups[book].append(doc)

        for book, docs in book_groups.items():
            print(f"Building index for {book} with {len(docs)} chunks...")
            self.indexes[book] = FAISS.from_documents(docs, self.embedding_model)

    def save_indexes(self, base_directory="faiss_indexes"):
        """
        Sauvegarde chaque index FAISS dans un dossier distinct.
        """
        os.makedirs(base_directory, exist_ok=True)
        for book, index in self.indexes.items():
            index_path = os.path.join(base_directory, book.replace(" ", "_"))
            index.save_local(index_path)
            print(f"Index saved: {index_path}")

    def load_indexes(self, base_directory="faiss_indexes"):
        """
        Charge tous les index FAISS depuis les fichiers sauvegardés.
        """
        self.indexes = {}
        for book_folder in os.listdir(base_directory):
            book_name = book_folder.replace("_", " ")
            print(f"Loading index for {book_name}...")
            index_path = os.path.join(base_directory, book_folder)
            self.indexes[book_name] = FAISS.load_local(
                index_path, self.embedding_model, allow_dangerous_deserialization=True
            )

    def search(self, query, books=None, nb_extracts=10, max_extracts_per_book=5):
        """
        Recherche dans un ou plusieurs livres et retourne les extraits avec les numéros de pages.
        """
        results = []
        search_books = books if books else self.indexes.keys()

        for book in search_books:
            if book in self.indexes:
                book_results = self.indexes[book].similarity_search_with_score(query, k=max_extracts_per_book)
                
                for doc, score in book_results:
                    doc.metadata["similarity_score"] = score
                
                results.extend(book_results)

        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)

        selected_docs = []
        book_counts = {book: 0 for book in search_books}  

        for doc, score in sorted_results:
            book = doc.metadata.get("source", "Unknown")
            if book_counts[book] < max_extracts_per_book:
                selected_docs.append(doc)
                book_counts[book] += 1

            if len(selected_docs) >= nb_extracts:
                break

        return selected_docs
