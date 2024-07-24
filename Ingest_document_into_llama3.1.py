import streamlit as st
from ollama import Client
import chromadb
import PyPDF2 as pdf
import tempfile
import os
from typing import Dict, List, Tuple

# Initialize Ollama client
client = Client(host='http://localhost:11434')

# Initialize ChromaDB client with local persistent storage
chroma_client = chromadb.PersistentClient(path="./chroma_db")


def extract_text_from_pdf(pdf_path: str) -> List[Tuple[int, str]]:
    result = []
    try:
        with open(pdf_path, 'rb') as f:
            pdf_reader = pdf.PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                result.append((page_num, text))
    except pdf.errors.DependencyError:
        st.error(
            "PyCryptodome is required for processing encrypted PDFs. Please install it using: pip install pycryptodome")
        return []
    except Exception as e:
        st.error(f"An error occurred while processing the PDF: {str(e)}")
        return []
    return result


def summarize_text(text: str) -> str:
    prompt = f"Please summarize the following text:\n\n{text}\n\nSummary:"
    response = client.generate(model="llama3.1:8b", prompt=prompt)
    return response['response']


def vectorize_text(text: str) -> List[float]:
    response = client.embeddings(model="mxbai-embed-large", prompt=text)
    return response["embedding"]


def store_in_chromadb(data: Dict[str, str], collection_name: str):
    try:
        collection = chroma_client.get_or_create_collection(name=collection_name)
        st.write(f"Collection '{collection_name}' created or accessed.")

        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for i, (key, value) in enumerate(data.items()):
            st.write(f"Processing item {i + 1}/{len(data)}: {key}")

            try:
                embedding = vectorize_text(value)
                st.write(f"Embedding generated for {key}")

                ids.append(str(i))
                embeddings.append(embedding)
                documents.append(value)
                metadatas.append({"page": key})

            except Exception as item_error:
                st.error(f"Error processing item {key}: {str(item_error)}")

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        st.write(f"All items added to ChromaDB")

        # Verify data was stored
        count = collection.count()
        st.write(f"Total items in collection after storage: {count}")

        if count == len(data):
            st.success(f"All {count} items successfully stored in ChromaDB.")
            return True
        else:
            st.warning(f"Only {count} out of {len(data)} items stored in ChromaDB.")
            return False
    except Exception as e:
        st.error(f"Error storing data in ChromaDB: {e}")
        return False


def verify_summaries(summaries: Dict[str, str]):
    st.write("Verifying summaries before storage:")
    for key, value in summaries.items():
        st.write(f"{key}: {value[:100]}...")  # Display first 100 characters of each summary

    if not summaries:
        st.warning("No summaries generated. Please check the PDF processing and summarization steps.")
        return False
    return True


def perform_auto_query(collection_name: str):
    query = """
    Infosys wants to drive desired behaviors and outcomes, which is the checklist of things 
    employees and managers should do to comply with CARE and VALUES documents. 
    We should merge that with the grading system.
    """
    query_embedding = vectorize_text(query)

    collection = chroma_client.get_collection(name=collection_name)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    if results['ids']:
        st.subheader("Relevant Information from the Document:")
        for i, (id, distance, document, metadata) in enumerate(zip(
                results['ids'][0], results['distances'][0],
                results['documents'][0], results['metadatas'][0]
        )):
            st.write(f"Excerpt {i + 1}:")
            st.write(f"Page: {metadata['page']}")
            st.write(f"Content: {document}")
            st.write(f"Relevance Score: {1 - distance}")
            st.write("---")
    else:
        st.write("No relevant information found in the document.")


def main():
    st.title("Infosys CARE and VALUES Document Analysis")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        with st.spinner("Processing PDF..."):
            page_texts = extract_text_from_pdf(tmp_file_path)

        if not page_texts:
            st.warning("Unable to process the PDF. Please ensure it's not encrypted and try again.")
        else:
            summaries = {}
            for page_num, text in page_texts:
                with st.spinner(f"Summarizing page {page_num + 1}..."):
                    summary = summarize_text(text)
                    summaries[f"Page {page_num + 1}"] = summary

            if verify_summaries(summaries):
                with st.spinner("Storing summaries in ChromaDB..."):
                    success = store_in_chromadb(summaries, "pdf_summaries")

                if success:
                    st.success("PDF processed and stored successfully!")
                    perform_auto_query("pdf_summaries")
                else:
                    st.error("Failed to store data in ChromaDB. Please try again.")
            else:
                st.error("Summary verification failed. Unable to store in ChromaDB.")

        os.unlink(tmp_file_path)


if __name__ == "__main__":
    main()