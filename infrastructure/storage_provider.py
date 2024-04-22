import os
from azure.storage.blob import BlobServiceClient

class CloudStorageProvider:

    def __init__(self) -> None:
        self.connection_string = os.environ["openaiyourdatastorage_STORAGE"]

    def read_blob(self, container_name:str, blob_name:str):
        try:            
            blob_name = blob_name.replace(container_name, "").lstrip("/")
            blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            downloaded_blob = blob_client.download_blob()
            return downloaded_blob.content_as_bytes()
        except Exception as e:
            print(f"An error occurred: {e}")
            raise e
