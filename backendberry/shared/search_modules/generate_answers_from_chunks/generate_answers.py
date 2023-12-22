import openai
import os
from dotenv import load_dotenv 
load_dotenv()

class GetAnswersFromChunks():
    def __init__(self) -> None:
        pass
    def get_answers_from_chunks(self,question,text_chunks)->str:
        openai.api_type = os.getenv("OPENAI_API_TYPE")
        self.userid=os.getenv("USERID")
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_version= os.getenv("HELICON_OPENAI_API_VERSION")
        openai.api_base=os.getenv("HELICON_OPENAI_API_BASE")
        self.engine=os.getenv("GENERATIVE_ENGINE")
        self.model=openai.ChatCompletion(engine=self.engine)
        prompt="""Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Use three sentences maximum and keep the answer as concise as possible.        
        """

        message_text = [{"role":"system","content":f"{prompt}"},
                        {"role":"user","content":f"{text_chunks}\nQuestion: {question}\nHelpful Answer:"}]
        
        completion = self.model.create(
        headers={
        "User-Id": self.userid
        },    
        engine=self.engine,
        model="gpt-3.5-turbo",
        messages = message_text,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
        )

        return completion['choices'][0]['message']['content']



