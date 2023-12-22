from sentence_transformers import CrossEncoder


class Reranker:
    def __init__(self) -> None:
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
        # CrossEncoder('BAAI/bge-reranker-large')
        # 'cross-encoder/ms-marco-MiniLM-L-12-v2'        
        pass
    def get_reranked_results(self,query,doc_list):
        result=list()        
        result = doc_list.apply(lambda v: (query, v['title'] + '\n' + v['text_chunk']), axis=1)       
        scores = self.model.predict(result.T.to_list())
        doc_list['scores']=scores
        doc_list=doc_list.sort_values(by='scores',ascending=False)
        # print(query,"--------",doc_list)
        return doc_list
