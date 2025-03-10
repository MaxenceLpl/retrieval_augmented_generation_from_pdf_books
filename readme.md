# **Retrieval-Augmented Generation (RAG) for Book Querying**  
This project implements a **Retrieval-Augmented Generation (RAG) pipeline** that allows users to query a set of books and retrieve **precise answers** along with **page references**. The system is designed using **LangChain, FAISS, OpenAI API, and Sentence Transformers**, providing **fast and accurate** document search.

---

## **Project Overview**  

This RAG system is built to:  
Extract text from **PDF books** while preserving **page numbers**.  
Split the text into **optimized chunks** to improve retrieval accuracy.  
Index the text using **FAISS**, a fast similarity search library.  
Retrieve the **most relevant excerpts** when a user asks a question.  
Generate an answer using **GPT-based models**, citing the **source book and page number**.
--- 

### **Choice of Embedding Model: `all-MiniLM-L6-v2`**  
To transform text into numerical vectors for similarity search, I use `all-MiniLM-L6-v2`, a model from `sentence-transformers`. This model is optimized for **semantic search**, providing a **good balance between accuracy and speed**. It allows FAISS to efficiently retrieve relevant text chunks based on meaning rather than exact word matches, ensuring **fast and precise query results** while keeping resource usage low.

### **1️ Extracting Text from PDFs**  
I used `PyPDF2` to **extract text page by page**, keeping track of where each page starts in the document. This allows me to later map any extracted text **back to its original page number**.  

### **2️ Splitting the Text into Meaningful Chunks**  
Once the text is extracted, we need to **split it into small excerpts** (called "chunks") to improve searchability. However, **splitting text incorrectly** (for example, mid-sentence) would lead to **incomplete answers**.  

To solve this, we use **`RecursiveCharacterTextSplitter`** from `LangChain`, which breaks the text **at natural points** (`"\n\n"`, `"\n"`, `" "`, `""`) while keeping **overlapping text** between chunks to preserve context.  

**What changed?**  
- Instead of randomly splitting, we now **maintain page numbers** for each chunk.  
- The system finds the **page range** of a chunk using `page_map`, ensuring **accurate citations** in the final response.  

---

### **3️ Indexing the Books for Fast Search**  
To make searches **fast**, we use **FAISS**, a **vector-based search engine** that stores **embeddings** of text excerpts instead of raw text. This allows us to **search by meaning**, rather than exact word matches.  

Each book gets **its own FAISS index**, allowing us to:  
- Search **within a single book**  
- Search **across multiple books**  
- Control **the balance of excerpts per book**  

**What changed?**  
- Before, all books were indexed together, making it hard to control **diversity in search results**.  
- Now, **separate indexes** allow us to retrieve **balanced results** (for example, when comparing Harry Potter and Katniss Everdeen).  

---

### **4️ Searching and Filtering the Best Excerpts**  
When a user asks a question, the system first **retrieves the most relevant excerpts** using FAISS. However, a key challenge was ensuring **results are diverse**, otherwise a query comparing **Harry Potter and Hunger Games** could return **only Harry Potter excerpts**.  

I solve this by:  
1. Searching **each book separately**  
2. Limiting the **max number of excerpts per book**  
3. Sorting by **relevance and diversity**  

**What changed?**  
- Instead of retrieving **only the top-scoring results**, we **balance** results across books.  
- If a book has **too many results**, we **limit** it to prevent it from dominating the answer.  

---

### **5️Generating a Precise Answer with AI**  
Once the system finds relevant excerpts, it **generates an answer** using **GPT-based models**.  

**Challenges:**  
- Avoiding hallucinations (GPT making up facts)  
- Ensuring it only uses retrieved text  

To fix this, I **rephrase the prompt** to:  
- Force GPT to only use provided excerpts  
- Ignore useless text  
- Infer missing details rigorously  

**What changed?**  
- The new prompt makes GPT **ignore irrelevant excerpts**.  
- Instead of saying "I don’t know," GPT **tries to infer the best answer** from the text.  

---

## **Project Structure**  

### **`src/` - Core Source Code**  
This folder contains the main scripts for text extraction, chunking, indexing, and querying.

### **`pdf_loader.py`**  
Extracts text **page by page** from a given **PDF book** and maintains a **mapping of character indices to page numbers**.

- **`load_pdf(pdf_path, source)`**  
  - Extracts text **per page** and keeps track of **where each page starts** in the text.  
  - Returns:
    - **Full book text**
    - **Page mapping (character index → page number)**  

---

### **`chunker.py`**  
Splits the **full book text** into **manageable chunks** while keeping **page metadata**.  

- **`split_text_into_documents(text, source, page_map, chunk_size=500, chunk_overlap=50)`**  
  - Uses **recursive text splitting** with **overlap** to improve retrieval.  
  - Keeps **page numbers** for each chunk by referencing `page_map`.  

---

### **`indexer.py`**  
Manages **FAISS indexes** for efficient search. Supports:  
**Saving and loading indexes**  
**Separate indexes per book**
**Cross-book retrieval**  

- **`build_indexes(documents)`** → Creates an **FAISS index for each book**.  
- **`save_indexes()`** → Saves indexes to disk.  
- **`load_indexes()`** → Loads saved indexes.  
- **`search(query, books=None, k=10)`** → Finds **the best excerpts** across selected books.  

---

### **`generator.py`**  
Handles **user queries** by retrieving the best excerpts and generating an **AI-powered response**.

- **`generate_answer(query, retrieved_docs, model="gpt-4o-mini", temperature=0.0)`**  
  - Uses **GPT API** to generate a response.  
  - Cites **source books and page numbers**.

---
