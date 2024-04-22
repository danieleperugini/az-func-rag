import json
import azure.functions as func
import logging

from application.document_service import DocumentService

app = func.FunctionApp()


@app.blob_trigger(arg_name="myblob", path="docs-input",connection="openaiyourdatastorage_STORAGE") 
def DocumentProcessor(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")
    document_service = DocumentService()
    document_service.process_document(blob_name=myblob.name)



@app.route(route="AskDocuments", auth_level=func.AuthLevel.FUNCTION)
def AskDocuments(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    user_request = req.params.get('req')
    if not user_request:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            user_request = req_body.get('req')

    if user_request:
        document_service = DocumentService()
        response = document_service.query_documents(user_request=user_request)
        json_response = json.dumps(response, indent = 4) 
        return func.HttpResponse(json_response)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a request in json body 'req' field",
             status_code=200
        )