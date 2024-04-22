import io
import os
from infrastructure.ai_provider import OpenAIProvider
from infrastructure.cosmosdb_provider import MongoDbProvider
from infrastructure.storage_provider import CloudStorageProvider
from infrastructure.text_helper import TextHelper

class DocumentService:
    
    def __init__(self) -> None:
        self.cloud_storage_provider = CloudStorageProvider()
        self.text_helper = TextHelper()
        self.openai_provider = OpenAIProvider()
        self.db_provider = MongoDbProvider(dbname=os.environ["cosmos_db_mongo_dbname"])
        self.VECTOR_FIELD = "chunk_vector"

    def process_document(self, blob_name:str):
        VECTOR_FIELD = "chunk_vector"

        blob_content = self.cloud_storage_provider.read_blob(container_name="docs-input", blob_name=blob_name)        
        bytes_content = io.BytesIO(blob_content)

        # todo: check if file is pdf
        file_object = self.text_helper.extract_text_from_pdf(file_name=blob_name, content=bytes_content)

        chunks = self.text_helper.chunk_documents([file_object])

        for chunk in chunks:
            embeddings = self.openai_provider.generate_embeddings(chunk["chunk"])
            if (embeddings):
                chunk[self.VECTOR_FIELD] = embeddings
        
        db_collection = os.environ["cosmos_db_mongo_collection"]

        self.db_provider.init_db(collection=db_collection, drop_collection_if_exists=False)
        self.db_provider.ensure_vector_index_exist(collection=db_collection, field=VECTOR_FIELD)
        self.db_provider.insert_many(collection=db_collection, data=chunks)

    def query_documents(self, user_request:str) -> str:
        user_request_embedding = self.openai_provider.generate_embeddings(text=user_request)
        documents_vector_search_results = self.db_provider.vector_search(
            collection_name=os.environ["cosmos_db_mongo_collection"],
            field_name=self.VECTOR_FIELD,
            query_embedding=user_request_embedding)
        
        llm_response = self.openai_provider.generate_completion(
            vector_search_results=documents_vector_search_results,
            user_prompt=user_request)
        return {
            "request": user_request,
            "response": llm_response
        }

        