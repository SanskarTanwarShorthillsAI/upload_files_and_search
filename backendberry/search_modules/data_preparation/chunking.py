import re
import tiktoken
from pathlib import Path

class CreateChunks:
    def __init__(self) -> None:
        pass
    
    def list_files_recursive(self,directory):
        path = Path(directory)
        file_path_list=list()
        for file_path in path.rglob('*'):
            if file_path.is_file():
                file_path_list.append(str(file_path))
                # print(file_path)  # Or do something with the file path
        return file_path_list

    def getCleanData(self,text):
        """
        clean the data and only keeps alphanumeric characters
        """
        text=re.sub(r'[^a-zA-Z0-9\s]', '', text)
        text=re.sub(r'\n+', '\n', text)
        return text
    
    def getlen(self,text):
        """
        calculate the length of chunks
        """
        if text:
            return len(text.split())
        return 0
    
    def num_tokens_from_string(self,string: str, encoding_name: str="cl100k_base") -> int:
        """Returns the number of tokens in a text string.
            for ada  use "cl100k_base"
            by default it will use "cl100k_base".
        """
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    

