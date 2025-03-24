from typing import List, Tuple, Any, Dict
import json
from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import OllamaEmbeddings

embedding = OllamaEmbeddings(  base_url='http://127.0.0.1:11434',
    model="llama3.2")
 

class ChatHistory:
    def __init__(self):

        self.history = []

    def add_interaction(self, user_input: str, response: str):
        interaction = {
            "user_input": user_input,
            "response": response
        }
        self.history.append(interaction)

    def save_history(self, file_path: str):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def load_history(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            self.history = json.load(f)

    def get_history(self) -> List[Dict[str, str]]:
        return self.history
    
class ChatRetriever:

        def __init__(self, db_path: str, model: str):
            self.embeddings = embedding
            self.vectorstore = Chroma(embedding_function=self.embeddings, persist_directory=db_path)

        def add_to_index(self, interactions: List[Dict[str, str]]):
            documents = [interaction["user_input"] + " " + interaction["response"] for interaction in interactions]
            self.vectorstore.add_texts(documents)

        def retrieve_similar(self, query: str, k: int = 5):
            return self.vectorstore.similarity_search(query, k=k)
