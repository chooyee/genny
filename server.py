from sanic import Sanic
from sanic.response import HTTPResponse, text, json
from sanic.request import Request
from sanic_ext import Extend
from sanic.log import logger
import os, time, datetime, logging, base64
from genny import NewPdf
from sanic.worker.manager import WorkerManager
from langchain.embeddings import HuggingFaceEmbeddings
from askgenny import Prompt

WELCOME_MESSAGE = r"""
Ask GENNY Anything
"""

print(WELCOME_MESSAGE)

LOGGING_CONFIG= logging.basicConfig(
    filename=datetime.datetime.now().strftime('log_%Y-%m-%d.log'),
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %I:%M:%S%p",
)
        
WorkerManager.THRESHOLD = 20000  # 这个值对应着 0.1s

#set embedding model
model_name = "sentence-transformers/all-mpnet-base-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)

app = Sanic(__name__, log_config=LOGGING_CONFIG)
app.config.CORS_ORIGINS = "*"
Extend(app)
app.config["DATA_FOLDER"] = "data"

app.static('/public', './public')

@app.get("/")
@app.ext.template("prompt.html")
async def hello_world(request):
    return {"seq": ["one", "two"]}

@app.post("/prompt")
async def prompt(request):
    result =Prompt(request.json["visitorid"], request.json["prompt"],request.json["chathistory"],embeddings)    
    return json(result)

@app.get("/hello")
async def typed_handler(request: Request) -> HTTPResponse:
    return text("Done.")

@app.route("/upload/pdf", methods=['POST'])
async def upload(request):
    dataFolder = app.config['DATA_FOLDER']
    visitorid = request.form.get('visitorid')
    fullPath = await write_to_file(dataFolder, request)
    # if os.path.exists(fullPath):
    #     print("File Exists:" + fullPath)
    # result = detect(fullPath)
    pickle = NewPdf(visitorid, fullPath, embeddings)
    result = {}
    result["msg"] = "success"
    result["pickle"] = pickle
    return json(result)


async def write_to_file(uploadFolder, request):   
    import aiofiles
    if not os.path.exists(uploadFolder):
        os.makedirs(uploadFolder)
    async with aiofiles.open(uploadFolder +"/"+request.files["file"][0].name, 'wb') as f:
        await f.write(request.files["file"][0].body)
    f.close()
    filename = request.files["file"][0].name
    fullPath = uploadFolder +"/"+ filename
    return fullPath

if __name__ == "__main__":
  
    app.run(host='0.0.0.0', port=8000)