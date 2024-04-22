import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pdfplumber

class TextHelper:

    def extract_text_from_pdfs(self, directory):
        docs = []
        # Traverse the directory and find PDF files
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.pdf'):
                    print(f"Processing file: {file}")
                    path = os.path.join(root, file)
                    # Extract text from the PDF
                    try:
                        with pdfplumber.open(path) as pdf:
                            text = ""
                            for page in pdf.pages:
                                text += page.extract_text() or ""  # Ensure we append empty string if no text
                            docs.append({'file_name': file, 'text': text})
                            print(text)
                    except Exception as e:
                        print(f"Failed to process {path}: {str(e)}")

        return docs
    
    def extract_text_from_pdf(self, file_name, content):
        try:
            with pdfplumber.open(content) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""  # Ensure we append empty string if no text
                return {
                    "file_name": file_name, 
                    "text": text
                }                
        except Exception as e:
            print(f"Failed to process {file_name}: {str(e)}")        

    def chunk_documents(self, docs):
        chunks = []
        for doc in docs:
            try:
                doc_chunks = self.chunk_text(doc['text'])
                for i, chunk in enumerate(doc_chunks):
                    chunks.append({'document_name': doc['file_name'], 'chunk': chunk.page_content, 'sequence': i+1})
            except Exception as e:
                print(f"Failed to chunk {doc['file_name']}: {str(e)}")

        return chunks

    def chunk_text(self, text):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 256,
            chunk_overlap  = 20,
            separators = ["\n\n", "\n"]
        )
        chunks = text_splitter.create_documents([text])
        return chunks