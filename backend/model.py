from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.llms import CTransformers
from langchain_ollama import OllamaLLM
from langchain.vectorstores import Pinecone
import pinecone

PINECONE_API_KEY = "2bd5fd9f-2c56-42f9-aa1b-037960262fff"
PINECONE_API_ENV = "aws-starter"

def load_pdf(data):
    loader = DirectoryLoader(data,
                             glob="*.pdf",
                             loader_cls=PyPDFLoader)
    documents = loader.load()
    return documents

extracted_data = load_pdf("data/")

#Create Text Chunks
def text_split(extracted_data):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap = 20)
    text_chunks = text_splitter.split_documents(extracted_data)
    return text_chunks

text_chunks = text_split(extracted_data)
len(text_chunks)

#Download embedding model
def download_embeddings():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embeddings

embeddings=download_embeddings()

query_result = embeddings.embed_query("Hello, world")
len(query_result)

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("quickstart")

#Initializing the Pinecone
pinecone.init(api_key=PINECONE_API_KEY,
              environment=PINECONE_API_ENV)

index_name="medical-chatbot"

#Creating Embeddings for Each of The Text Chunks & storing
docsearch=Pinecone.from_texts([t.page_content for t in text_chunks], embeddings, index_name=index_name)

#If we already have an index we can load it like this
docsearch=Pinecone.from_existing_index(index_name, embeddings)

query = "What are Allergies"

docs=docsearch.similarity_search(query, k=3)

print("Result", docs)

prompt_template="""
Use the following pieces of information to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}
Question: {question}

Only return the helpful answer below and nothing else.
Helpful answer:
"""

PROMPT=PromptTemplate(template=prompt_template, input_variables=["context", "question"])
chain_type_kwargs={"prompt": PROMPT}

model=CTransformers(model="model/llama-3.1-7b-chat.ggmlv3.q4_0.bin",
                  model_type="llama",
                  config={'max_new_tokens':512,
                          'temperature':0.8})

model = OllamaLLM(model="llama3.1")

qa=RetrievalQA.from_chain_type(
    llm=model, 
    chain_type="stuff", 
    retriever=docsearch.as_retriever(search_kwargs={'k': 2}),
    return_source_documents=True, 
    chain_type_kwargs=chain_type_kwargs)

while True:
    user_input=input(f"Input Prompt:")
    result=qa({"query": user_input})
    print("Response : ", result["result"])