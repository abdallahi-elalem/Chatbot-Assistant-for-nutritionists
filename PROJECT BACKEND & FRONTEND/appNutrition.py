from flask import Flask, request
from flask_cors import CORS
import uuid

from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM
from langchain_chroma import Chroma

from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PDFPlumberLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.schema.messages import HumanMessage, AIMessage
from langchain_chroma import Chroma
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.schema.document import Document
from langchain.storage import InMemoryStore
from langchain.chains import LLMChain
from ChatHistory import  ChatHistory, ChatRetriever
from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import OllamaEmbeddings

app = Flask(__name__)
CORS(app)


 
cached_llm = OllamaLLM( ## model de generation 
    base_url='http://127.0.0.1:11434', ## localhost http://127.0.0.1:11434/
    model="llama3.2")

embedding = OllamaEmbeddings(  base_url='http://127.0.0.1:11434',
    model="llama3.2")
 
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1024, chunk_overlap=80, length_function=len, is_separator_regex=False
)
 
raw_prompt = PromptTemplate.from_template(
    """
    <s>[INST] You are an AI assistant specialized in reticular chemistry, tasked with aiding a human apprentice on a
research project aimed at developing a novel aluminum MOF using a new linker, BTB-X. Firstly, you are
expected to thoroughly comprehend the standard practices in reticular chemistry. This understanding
should come from both the text provided below and your existing domain knowledge in reticular
chemistry. Afterward, you should propose 5 broad stages of research development pertinent to this
project. For each stage, clearly define the objective or the indication of its completion. Consider this
process as analogous to writing Python code. In coding, the whole project is divided into several
generic functions, where the testing of subsequent functions relies on the completion of previous ones.
Similarly, we need to guide our apprentice, who has limited knowledge of reticular chemistry, in
completing tasks sequentially, and ultimately mastering the standard practice in reticular chemistry.
In addition, below are some additional notes regarding this research:
1) The desired linker is not readily available, but we have designed the structures.
2) Our aim is to discover and understand a new topology or structure of Al MOF that has not been
found before through screening synthesis conditions.
3) We're interested in analyzing the structure to gain a deeper understanding on how this structure
forms rather than focusing on real-world applications.
4) We are equipped with a 96-well high-throughput plate for MOF synthesis and screening, and a
variety of analytical instruments including PXRD, SXRD, TGA, UV-Vis, and IR for thorough analysis. We
also have the capability to perform proton and carbon NMR spectroscopy. If needed, more specialized
techniques such as electron diffraction (ED) and mass spectroscopy (MS) can be arranged upon
request. Additionally, we have a standard hood for organic synthesis, and we're able to procure most
commercially available materials as required.
“””
■ WORKFLOW IN THE PRACTICE OF RETICULAR CHEMISTRY
……
… the correct execution of the analysis and a thorough description of the results.
“””
Should you have any questions or find any aspects of this prompt unclear, please include your inquiries
in your response.

  



    [INST]
    Contexte : {context}
    Historique : {history}
    Question : {question}
    Réponse :
    [/INST]
    """
)


 
 
 
class Generation:
    def __init__(self):
        self.history = []
        self.embedding = embedding ## text -- vector
        self.vector_store = Chroma(persist_directory="db", embedding_function=self.embedding)  ## base 
        self.cached_llm = cached_llm 
        self.retriever = ChatRetriever(db_path="db", model="llama3.2") ## 

    def format_history(self, chat_history):
        print(f"Formatted history: {chat_history.get_entries()}")

        formatted_history = "\n".join(
            [f"User: {str(entry.get('user_input', ''))}\nAssistant: {str(entry.get('response', ''))}" for entry in chat_history.get_entries()]
        )
        return formatted_history
    
    def add_to_history(self, user_input, response):
        self.history.append({'user_input': user_input, 'response': response})
    
    def summarize_text(self, text_element):
        prompt = f"Summarize the following text directly without saying 'Here is a summary.' If the text or summary is missing, return an empty response:\n\n{text_element}\n\nSummary:"

        response = self.cached_llm.invoke(prompt)
        return response
    
    def add_documents_to_retriever(self, summaries):
        summary_docs = [Document(page_content=s) for s in summaries]
        self.vector_store.add_documents(summary_docs)

    
    def format_history(self, chat_history):
        print(f"Formatted history: {chat_history}")

        formatted_history = "\n".join(
            [f"User: {entry['user_input']}\nAssistant: {entry['response']}" for entry in chat_history]
        )
        return formatted_history
    
    def add_to_history(self, user_input, response):
        self.history.append({'user_input': user_input, 'response': response})
    
     
    
    def add_documents_to_retriever(self, summaries):
        summary_docs = [Document(page_content=s) for s in summaries]
        self.vector_store.add_documents(summary_docs)
    
    def retrieve_with_history(self, query, chat_history):
        formatted_history = self.format_history(chat_history)
        full_query = f"{formatted_history}\n{query}"
        return self.retriever.retrieve_similar(full_query)
    
    def handle_ai_query(self, query):
        response = self.cached_llm.invoke(query)
        self.add_to_history(query, response)
        return {"answer": response}
    
    def handle_ask_pdf_query(self, question):
        context_docs = self.retrieve_with_history(question, self.history)
        context = " ".join([doc.page_content for doc in context_docs])
        history = self.format_history(self.history)
        #prompt = PromptTemplate.from_template(prompt_template)
        explanation_chain = LLMChain(llm=self.cached_llm, prompt=raw_prompt)
        result = explanation_chain.invoke({'context': context, 'history': history, 'question': question})
        self.add_to_history(question, result['text'])
        print('result',result)
        return result['text']
    
    
    def process_chunk_batch(self,batch):
        for i, chunk in enumerate(batch):
            print('batch',i)
            text_summary = self.summarize_text(chunk.page_content)
            batch[i].page_content = text_summary
        return batch
            
    def process_pdf(self, file):
        file_name = file.filename
        save_file = "pdf/" + file_name
        file.save(save_file)
        print(f"filename: {file_name}")
        
        # Charge et divise le PDF en documents
        loader = PDFPlumberLoader(save_file)
        docs = loader.load_and_split()
        
        # Divise les documents en chunks
        chunks = text_splitter.split_documents(docs)
    
        chunks=chunks[5:]
        print('chunksto',chunks)
       # Traite les chunks par lots de 100
        while len(chunks) > 50:
            batch = chunks[:50]
            print('chunks',len(chunks))
            batchsummaryes=self.process_chunk_batch(batch)
            self.vector_store.add_documents(batchsummaryes)
            chunks = chunks[50:]
        
        # Traite les chunks restants
        if chunks:
            self.process_chunk_batch(chunks)
        
        return {
            "status": "Successfully Uploaded",
            "filename": file.filename,
            "doc_len": len(docs),
            "chunks": len(chunks),
        }
    
    

    def handle_ai_query(self, query):
        response = self.cached_llm.invoke(query)
        self.add_to_history(query, response)
        return {"answer": response}
    
     

gen = Generation()

@app.route("/ai", methods=["POST"])
def aiPost():
    print("Post /ai called")
    json_content = request.json
    query = json_content.get("query")

    print(f"query: {query}")

    response = gen.handle_ai_query(query)

    print(response)

    return response

@app.route("/ask_pdf", methods=["POST"])
def askPDFPost():
    print("Post /ask_pdf called")
    json_content = request.json
    question = json_content.get("query")

    print(f"query: {question}")

    response = gen.handle_ask_pdf_query(question)
    
    return response

@app.route("/pdf", methods=["POST"])
def pdfPost():
    file = request.files["file"]
    response = gen.process_pdf(file)
    return response

def start_app():
    app.run(host="0.0.0.0", port=8080, debug=True)

if __name__ == "__main__":
    start_app()
