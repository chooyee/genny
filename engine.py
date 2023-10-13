import os
import sys

from langchain.llms import Replicate
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain

# Replicate API token
os.environ['REPLICATE_API_TOKEN'] = "r8_0CITZrzocjRMungTi7uQFP68dsrcswX0ZJG1D"

# load the document as before
loader = PyPDFLoader('./docs/PD-RMiT-June2023.pdf')
documents = loader.load()

#break docment into chunk
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
all_splits = text_splitter.split_documents(documents)

#set embedding model
model_name = "sentence-transformers/all-mpnet-base-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)

#embedding database
vectordb = Chroma.from_documents(
  documents,
  embedding=embeddings,
  persist_directory='./data'
)
vectordb.persist()

# Initialize Replicate Llama2 Model
llm = Replicate(
    model="a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5",
    input={"temperature": 0.75, "max_length": 4000}
)

# local_path = ("./models/GPT4All/ggml-gpt4all-j-v1.3-groovy.bin")

# # initialize the LLM and make chain it with the prompts

# llm = GPT4All(
#     model=local_path, 
#     backend="llama", 
# )

# Set up the Conversational Retrieval Chain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm,
    vectordb.as_retriever(search_kwargs={'k': 2}),
    return_source_documents=True
)

# Start chatting with the chatbot
chat_history = []
while True:
    query = input('Prompt: ')
    if query.lower() in ["exit", "quit", "q"]:
        print('Exiting')
        sys.exit()
    result = qa_chain({'question': query, 'chat_history': chat_history})
    print('Answer: ' + result['answer'] + '\n')
    chat_history.append((query, result['answer']))