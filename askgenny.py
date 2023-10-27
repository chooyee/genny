import os, time, pickle, json
from sanic.log import logger
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Chroma
from config.config import globalConfig

os.environ['REPLICATE_API_TOKEN'] = "r8_0CITZrzocjRMungTi7uQFP68dsrcswX0ZJG1D"

def Prompt(visitorid,doclabel, query, chatHistory, embeddings):

    print (globalConfig["mysql"]["host"])

    processTime = {}
    dataPath = f'./data/{doclabel}'
    picklePath = f'{dataPath}/llm.pickle'
    #convert to tuple
    chat_history = []
    for c in chatHistory:
        chat_history.append((c[0], c[1]))
    
    start_time = time.time()
    vectordb = Chroma(persist_directory=dataPath, embedding_function=embeddings)
    end_time = time.time()
    elapsed_time = end_time - start_time
    processTime["vectordb"] = str(elapsed_time)

    start_time = time.time()
    # Load llms from the pickle file
    with open(picklePath, 'rb') as f:
        llm = pickle.load(f)
    end_time = time.time()
    elapsed_time = end_time - start_time
    processTime["pickle"] = str(elapsed_time)

    start_time = time.time()
    # Set up the Conversational Retrieval Chain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm,
        vectordb.as_retriever(search_kwargs={'k': 2}),
        return_source_documents=True
    )
    end_time = time.time()
    elapsed_time = end_time - start_time
    processTime["qa_chain"] = str(elapsed_time)

    start_time = time.time()
    queryResult = qa_chain({'question': query, 'chat_history': chat_history})
    end_time = time.time()
    elapsed_time = end_time - start_time
    processTime["queryResult"] = str(elapsed_time)

    chat_history.append((query, queryResult['answer']))
    result = {}
    result["answer"] = queryResult['answer']
    result["chat_history"] = chat_history
    result["elapsed_time"] = processTime
    return result

