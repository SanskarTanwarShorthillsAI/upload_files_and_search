from dotenv import load_dotenv 
import weaviate
import os
load_dotenv() 
WEVIATE_HOST=os.getenv("WEAVIATE_HOST")
WEAVIATE_API_KEY=os.getenv("WEAVIATE_API_KEY")    

class Indexing:
    def __init__(self) -> None:
        CLIENT=weaviate.Client(
            url=WEVIATE_HOST,
            auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY)
        )  
        self.client=CLIENT
        pass
    
    def index_data_to_weaviatedb(self,data_list,index_name):
        """
        indexing in batch for weaviate db
        """
        # Configure a batch process
        self.client.batch.configure(batch_size=1000,
                            num_workers=4)  # Configure batch
        with self.client.batch as batch:
            # Batch import all Questions
            for i,d in enumerate(data_list):
                print(f"importing data: {i+1}")
                properties = d['properties']
                batch.add_data_object(properties, index_name, vector=d["vector"])



