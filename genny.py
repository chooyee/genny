import os, shutil
from sanic.log import logger
from langchain.llms import Replicate
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader

import pickle

# Replicate API token
os.environ['REPLICATE_API_TOKEN'] = "r8_0CITZrzocjRMungTi7uQFP68dsrcswX0ZJG1D"

def NewPdf(visitorid, fullPath, embeddings):
    """Read the image into OpenCV then detect human face. Return as base64"""
    logger.info('NewPdf: ' + visitorid)

    dataPath = f'./data/{visitorid}'

    # if os.path.isdir(dataPath):
    #     shutil.rmtree(dataPath)

    try:
        # load the document as before
        loader = PyPDFLoader(fullPath)
        documents = loader.load()

        #break docment into chunk
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
        all_splits = text_splitter.split_documents(documents)

        #set embedding model
        # model_name = "sentence-transformers/all-mpnet-base-v2"
        # embeddings = HuggingFaceEmbeddings(model_name=model_name)

        #embedding database
        vectordb = Chroma.from_documents(
            all_splits,
            embedding=embeddings,
            persist_directory= dataPath
        )
        
        vectordb.persist()

        # Initialize Replicate Llama2 Model
        # meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3
        # a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5
        # meta/llama-2-13b-chat:f4e2de70d66816a838a89eeeb621910adffb0dd0baba3976c96980970978018d
        llm = Replicate(
            model="meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
            input={"temperature": 1.25, "max_length": 4000, "max_new_tokens":4000}
        )

        pickleFile = f'{dataPath}/llm.pickle'

        with open(pickleFile, 'wb') as f:
            pickle.dump(llm, f)

        return pickleFile
    except Exception as e:
        logger.error(f'NewPdf error: {e}')
        raise

def getFileName(path_str):
    filename_without_ext = os.path.splitext(os.path.basename(path_str))[0]
    return filename_without_ext
