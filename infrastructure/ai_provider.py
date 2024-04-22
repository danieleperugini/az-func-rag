import os
from openai import AzureOpenAI


class OpenAIProvider:
    def __init__(self) -> None:
        self.azure_openai_client = AzureOpenAI(
            api_key=os.environ["openai_api_key"], 
            azure_endpoint=os.environ["openai_api_endpoint"], 
            api_version=os.environ["openai_api_version"]
        )

    def generate_embeddings(self, text:str):
        response = self.azure_openai_client.embeddings.create(input=text, model=os.environ['openai_embeddings_deployment'])
        embeddings =response.model_dump()
        return embeddings['data'][0]['embedding']

    def generate_completion(self, vector_search_results, user_prompt):
        system_prompt = '''
        Sei un assistente di HardwareTools Spa, azienda produttrice di utensileria. 
        Il tuo ruolo è quello di dare informazioni sul catalogo prodotti aziendale.
        Rispondi solo alle domande relative alle informazioni fornite di seguito.
        Scrivi due righe di spazio bianco tra ogni risposta nell'elenco.
        Cita sempre il nome documento da cui hai tratto la risposta.
        Se non sei sicuro di una risposta, puoi dire "Non lo so" o "Non sono sicuro" e consigliare agli utenti di cercare da soli.
        Fornisci solo risposte che sono parte dei seguenti prompt.
        Alla fine ringrazia il cliente da parte di HardwareTools Spa.
        Questa è la base di conoscenza che devi utilizzare:
        ###
        '''

        for item in vector_search_results:
            system_prompt += '\n' + " - nome documento: " + item['document']['document_name'] + " -> contenuto documento: " + item['document']['chunk'] 
        system_prompt += '\n'
        system_prompt += "###"

        # print(system_prompt)

        messages=[{"role": "system", "content": system_prompt}]
        
        # for item in vector_search_results:
            # messages.append({"role": "system", "content": item['document']['content']})

        messages.append({"role": "user", "content": user_prompt})

        response = self.azure_openai_client.chat.completions.create(
            model=os.environ['openai_completions_deployment'], 
            messages=messages,
            temperature=0)
        
        model_dump = response.model_dump()
        return model_dump['choices'][0]['message']['content']