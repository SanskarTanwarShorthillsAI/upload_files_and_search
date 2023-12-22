from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import os
import json
import pandas as pd 
from search_modules.embedding_model.get_embedding import CreateEmbeddings
from search_modules.generate_answers_from_chunks.generate_answers import GetAnswersFromChunks
from search_modules.intent.get_query_intent import GetQueryIntent
from search_modules.reranking.reranking import Reranker
import weaviate
from hashlib import sha256
from dotenv import load_dotenv 
load_dotenv()

class SearchUi:
    def __init__(self) -> None:
        auth_config=weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY"))
        self.client = weaviate.Client(
                url=os.getenv("WEAVIATE_HOST"),   
            auth_client_secret=auth_config
        )
        pass
    
   
    @staticmethod
    def get_load_embedding_model():
        embeddings=CreateEmbeddings()
        return embeddings
    
  
    @staticmethod    
    def get_load_reranking_model():
        reranker=Reranker()
        return reranker
    
    
    def search(self,query,index_name,query_embedding,alpha):
        response = (
            self.client.query
            .get(index_name, ["title", "text_chunk","file_path"])
            .with_hybrid(
                query=query,
                vector=query_embedding,
                alpha=alpha,
                properties=["title^5","text_chunk"]
            )
            .with_additional('score')
            .with_limit(1000)
            .do()
            )
        return response

# from rest_framework.authentication import BaseAuthentication
# from rest_framework.exceptions import AuthenticationFailed

# class StaticTokenAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         # Get the token from the request headers
#         # token = request.headers.get('Authorization')
#         data = json.loads(request.body.decode('utf-8'))
#         query = data.get('query', '')
#         received_hash = data.get('hashedData', '')
#         expected_hash = hash_data(query)
#         # key = os.getenv("SECRET_API_KEY")
#         # print(token)
#         print(received_hash)
#         print(expected_hash)
#         # print(f'Token {key}')
#         # Check if the token matches your static token
#         # if token == f'Token {key}':
#         if received_hash == expected_hash:
#             # If the token is valid, return a tuple of (user, None)
#             return (None, None)
        
#         # If the token is invalid, raise AuthenticationFailed
#         raise AuthenticationFailed('Invalid token')

@api_view(['POST'])
# @authentication_classes([StaticTokenAuthentication])
def search_api(request):
    """
    API endpoint for handling search requests.

    Parameters:
        - request: Django request object containing search query in the request body.

    Returns:
        - Response: JSON response containing search results.
    """
    try:
        # Get the query from the request data
        data = json.loads(request.body.decode('utf-8'))
        query = data.get('query', '')
        alpha=0.90
        generate_answer=GetAnswersFromChunks()
        # intent detection
        get_query_intent=GetQueryIntent()
        intent=get_query_intent.get_query_intent(query).strip().lower()        
        if len(query)!=0 and (intent=='keyword' or intent.__contains__('keyword')):
            alpha=0.10
        #######
        
        # Run the provided code
        search_ui = SearchUi()
        index_name = "Search_with_pdf"
        query_embedding = search_ui.get_load_embedding_model().get_embeddings(query)
        json_data = search_ui.search(query, index_name, query_embedding,alpha)

        # Additional lines to process and filter the results
        df_search = pd.DataFrame(json_data['data']['Get'][f'{index_name}'])
        # df_search = df_search.drop_duplicates('title')
        df_search = df_search.head(30)
        text_chunks=df_search['text_chunk']
        context=""
        for text_chunk in text_chunks[:3]:
            context+='\n\n'+text_chunk
        print("context------",context)
        df_search = search_ui.get_load_reranking_model().get_reranked_results(query, df_search)
        
        generative_answer=generate_answer.get_answers_from_chunks(query,context)

        # print(text_chunks)
        print(generative_answer)

        # Add the generative answer at the top of the DataFrame
        df_search = pd.concat([pd.DataFrame([{'title': 'Generative Answer', 'text_chunk': generative_answer, "_additional": {"score": "0"},"file_path": "Generative Answer","scores": 0}]), df_search])

        print(df_search)

        # Convert the DataFrame to JSON
        json_results = df_search.to_dict(orient='records')

        return Response({'results': json_results})
        # return Response({"results": json_data}) # For Testing Pagination
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=500)


# def hash_data(query):
#     # Replace with your hashing algorithm (SHA-256 in this example)
#     return sha256((query + os.getenv("SECRET_API_KEY")).encode()).hexdigest()