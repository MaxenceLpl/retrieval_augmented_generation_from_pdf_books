# src/generator.py
import openai

from secrets_variables import openai_api_key
from src.prompts import system, prompt

def generate_answer(query, context_documents, model="gpt-4o-mini", temperature=0.0):
    """
    Génère une réponse en utilisant l'API OpenAI à partir d'une question et d'extraits'.
    """
    # Concaténer les documents extraits pour fournir du contexte
    context = "\n\n".join([
        f"Source: {doc.metadata.get('source', 'Inconnu')}, Page: {doc.metadata.get('page_start', 'N/A')}\n{doc.page_content}"
        for doc in context_documents
    ])

    # Construire le prompt pour gpt
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt +            
            "### Extraits :\n\n"
            f"{context}\n\n"
            f"### Question : {query}"
        }
    ]

    try:
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Error while generating answer:", e)
        return ""

