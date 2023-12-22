from search_modules.document_loader.loader import DocumentLoaders
from search_modules.embedding_model.get_embedding import CreateEmbeddings
from search_modules.data_preparation.chunking import CreateChunks
from search_modules.index_data.indexing import Indexing
import time
import pandas as pd
from langchain.text_splitter import SpacyTextSplitter
import os
import concurrent.futures
import tempfile

class FileIndexer:
    def __init__(self, index_name):
        self.index_name = index_name
        # self.directory_to_scan = directory_to_scan
        self.chunks = CreateChunks()
        self.indexing = Indexing()
        self.embeddings = CreateEmbeddings()

    # def convert_to_pdf(self, input_file):
    #     """
    #     Convert supported document files to PDF using LibreOffice.

    #     Args:
    #         input_file (str): Full path of the input file.

    #     Returns:
    #         tuple: (str, str) Full path to the saved PDF file and the original file path.
    #     """
    #     try:
    #         # Get the file extension
    #         file_extension = os.path.splitext(input_file)[-1].lower()
    #         file_path = input_file

    #         # Add all the file extension present in your directory
    #         supported_formats = ["docx", "doc", "txt", "pptx", "docm", "xlsx", "pdf", "ppt"]

    #         if file_extension[1:] not in supported_formats:
    #             raise ValueError(f"Unsupported file format: {file_extension}")

    #         # Create a temporary directory
    #         temp_dir = tempfile.mkdtemp()

    #         # Command to convert the file to PDF using LibreOffice
    #         convert_command = [
    #             "libreoffice",
    #             "--headless",
    #             "--invisible",
    #             "--convert-to",
    #             "pdf",
    #             "--outdir",
    #             temp_dir,
    #             input_file
    #         ]

    #         # Execute the conversion command
    #         result = subprocess.run(convert_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    #         # Get the generated PDF file
    #         pdf_filename = os.path.splitext(os.path.basename(input_file))[0] + ".pdf"
    #         pdf_path = os.path.join(temp_dir, pdf_filename)

    #         return pdf_path, file_path

    #     except Exception as e:
    #         print(f"Error converting {input_file} to PDF: {str(e)}")
    #         error_file = "error_file_change.txt"
    #         with open(error_file, "a") as error_log:
    #             error_log.write("Filename : "+ os.path.basename(file_path) +", Exception :"+ str(e) + "\n")
    #         return None

    def create_input_data_embeddings_for_indexing(self, file_path):
        """
        enter the data location and it will return  the embeddings and coressponding title,page_no,file name, text chunks &  file url/path
        vector : title + text_chunks                 
        """    
        try:
            embeddings_list=[]
            # Calling convert_to_pdf() function :
            # pdf_path,filename = convert_to_pdf(file_path)
            pdf_path=file_path
            filename=file_path
            loader=DocumentLoaders(pdf_path).getDocumentsLoader()    
            text_splitter=SpacyTextSplitter(
                    chunk_size = 800,
                    chunk_overlap  = 200,
                    length_function = len,
                    add_start_index = False,
                    max_length=3000000
            )   
            text_chunks=loader.load_and_split(text_splitter=text_splitter)
            print(f"text chunks : {text_chunks}") 
            # chunk_to_be_added=chunks.getCleanData(text_chunks[0].page_content)
            chunk_to_be_added=text_chunks[0].page_content
            # page_number=text_chunks[0].metadata['page_number']
            total_token = 0
            istoaddflag=False
            for idx in range(len(text_chunks)):
                #time taken in adding a chunk
                b=time.time()
                # if chunk_to_be_added=='':
                #     # chunk_to_be_added+=" "+chunks.getCleanData(text_chunks[idx].page_content)
                #     chunk_to_be_added+=" "+text_chunks[idx].page_content

                # if istoaddflag:
                #     # chunk_to_be_added+=" "+chunks.getCleanData(text_chunks[idx].page_content)
                #     chunk_to_be_added+=" "+text_chunks[idx].page_content

                # # if not istoaddflag:
                # #     page_number=text_chunks[idx].metadata['page_number']
                
                # if chunks.getlen(chunk_to_be_added)<=200 and idx!=len(text_chunks)-1:            
                #     istoaddflag=True
                #     continue
                # if chunks.getlen(chunk_to_be_added)<=200 and idx==len(text_chunks)-1:
                #     # chunk_to_be_added=embeddings_list[len(embeddings_list)-1]['properties']['text_chunk']+" "+chunks.getCleanData(text_chunks[idx].page_content)            
                #     chunk_to_be_added=embeddings_list[len(embeddings_list)-1]['properties']['text_chunk']+" "+text_chunks[idx].page_content           
                chunk_to_be_added=text_chunks[idx].page_content
                b = time.time() - b
                data_dict=dict()
                final_data_dict=dict()
                # Updating the filepath 
                text_chunks[idx].metadata['source']=filename
                data_dict['file_path']=text_chunks[idx].metadata['source']
                # Updating the filename
                text_chunks[idx].metadata['filename']=os.path.basename(filename)
                data_dict['title']=text_chunks[idx].metadata['filename']
                data_dict['text_chunk']=chunk_to_be_added
                #Adding page_number in data_dict
                # data_dict['page_number']=page_number 
            
                final_data_dict['filename']=text_chunks[idx].metadata['filename']
                final_data_dict['properties']=data_dict
                

                #Time taken in embedding
                c = time.time()
                final_data_dict['vector']=self.embeddings.get_embeddings(data_dict['title']+chunk_to_be_added) #updated
                c = time.time() - c
                final_data_dict['word_count_per_chunk']=self.chunks.getlen(chunk_to_be_added)
                final_data_dict['time_in_chunk_added'] = str(b) 
                final_data_dict['time_in_embedding'] = str(c) 
                final_data_dict['token_length_per_chunk']=self.chunks.num_tokens_from_string(chunk_to_be_added,"cl100k_base")
                total_token += final_data_dict['token_length_per_chunk']
                embeddings_list.append(final_data_dict)
                # istoaddflag=False
                # chunk_to_be_added=''
            return embeddings_list,total_token
        except Exception as e:
            error_log_file="error_log.xlsx"
            # Log the error and chunk information to an Excel file
            error_data = {
                'Filename': [os.path.basename(file_path)],
                'Chunk': [text_chunks[0].page_content if text_chunks else ''],
                'Error': [str(e)]
            }
            error_df = pd.DataFrame(error_data)
            if not os.path.exists(error_log_file):
                error_df.to_excel(error_log_file, index=False)
            else:
                with pd.ExcelWriter(error_log_file, engine='openpyxl', mode='a') as writer:
                    error_df.to_excel(writer, index=False, header=False)
            raise


    def process_file(self, file_path):
        """
        Process a file for indexing.

        Args:
        - file_path (str): Path to the file for indexing.

        Embeds data and indexes to Weaviate.
        If an exception occurs, logs file name and exception details to 'error_file.txt'.

        """
        try:
            print(f"file for indexing - {file_path}")            
            data_list,total_token = self.create_input_data_embeddings_for_indexing(file_path)
            df = pd.DataFrame(data_list)
            df.to_excel("cost_estimation.xlsx")            
            # q = time.time() - t
            # print(f"time taken in embedding {q}")
            self.indexing.index_data_to_weaviatedb(data_list, self.index_name)
            # s = time.time() - t
            # print(f"total time taken {s}")
            print(f"total token :{total_token}")
        
        except Exception as e:
            print(e)
            # Log the file name where the error occurred
            # error_file = "error_file.txt"
            # with open(error_file, "a") as error_log:
            #      error_log.write("Filename : "+ file_path +", Exception :"+ e + "\n")

    def create_indexing(self):
        file_path_list = self.chunks.list_files_recursive(self.directory_to_scan)
        self.process_file(file_path_list[0])
        # Additional logic for processing batches if needed
        # ...

    def run_indexing(self):
        t = time.time()
        self.create_indexing()
        print("final time for indexing", time.time() - t)




# fileupload/views.py
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from indexing_docs import process_file
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import time
@api_view(['POST'])
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('myFile'):
        uploaded_file = request.FILES['myFile']
        file_indexer = FileIndexer(index_name="search_with_pdf")
        # Read the content of the file
        file_content = uploaded_file.read()
        # print(file_content)
        # Save the file to a temporary location
        # print(uploaded_file)
        # file_path = default_storage.save('temp/' + uploaded_file.name, ContentFile(uploaded_file.read()))
        # print(file_path)
        # Create the temporary directory if it doesn't exist
        temp_dir = os.path.join(settings.BASE_DIR, 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        # Save the PDF content to a temporary file
        temp_pdf_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_pdf_path, 'wb') as temp_pdf_file:
            temp_pdf_file.write(file_content)
            
        try:
            t=time.time()
            # Process the file for indexing
            file_indexer.process_file(temp_pdf_path)
            t=time.time() -t

            print(t)
            # You can also remove the temporary file if needed
            # default_storage.delete(file_path)

            return Response({'message': 'File received and indexed successfully.'}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error indexing file: {str(e)}")

            # You might want to handle the error more gracefully, e.g., log it or return an error response.
            return Response({'message': 'Error indexing file.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'Bad request.'}, status=status.HTTP_400_BAD_REQUEST)

