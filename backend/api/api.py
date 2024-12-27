import sys
import os
import json
import asyncio
import aiofiles
from fastapi import BackgroundTasks, FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from llama_index.core.schema import Document as LLamaDocument
from backend import Application, QuerySession, QueryState, Query

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

application = Application()
api = FastAPI()
api.mount("/static", StaticFiles(directory="backend/api/static"), name="static")
templates = Jinja2Templates(directory="backend/api/templates")
query_sessions: dict[str, QuerySession] = {}

# Create 'uploads' directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Register the API routes here
# Ping route (for testing)
@api.get('/api/ping')
async def ping():
    return 'pong'

@api.get('/api/texts/{fragment_id}')
async def get_text(fragment_id: str):
    """
    Flask API endpoint to retrieve a text document using fragement id.
    """
    try:
        # Get the document using the fragment id
        text = application.get_all_text_from_fragment_id(fragment_id)
        return {"text": text}
    except Exception:
        raise HTTPException(status_code=404, detail="Document not found")

async def process_query_receiver(websocket: WebSocket, client_id: str):
    while client_id in query_sessions:
        data = await websocket.receive_text()
        if query_sessions[client_id].state == QueryState.NONE:
            try:
                query = json.loads(data, object_hook=lambda d: Query(**d))
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                continue
            query_sessions[client_id] = QuerySession(QueryState.SEARCHING_LOCAL)
            await asyncio.sleep(0) # Allow the consumer to process the query
            await application.process_query(query.query, query_sessions, client_id)

async def process_query_sender(websocket: WebSocket, client_id: str):
    while client_id in query_sessions:
        state = query_sessions[client_id].state
        if state in {QueryState.SEARCHING_LOCAL, QueryState.SEARCHING_INTERNET}:
            await websocket.send_json(query_sessions[client_id].__dict__)
            query_sessions[client_id].state = QueryState.PENDING
        elif state in {QueryState.SUCCESS, QueryState.ERROR}:
            await websocket.send_json(query_sessions[client_id].__dict__)
            query_sessions[client_id].state = QueryState.NONE
        await asyncio.sleep(0)

@api.websocket('/api/process-query')
async def process_query(websocket: WebSocket):
    client_id = websocket.headers.get('Sec-WebSocket-Key')
    query_sessions[client_id] = QuerySession(QueryState.NONE)
    await websocket.accept()
    producer = asyncio.create_task(process_query_sender(websocket, client_id))
    consumer = asyncio.create_task(process_query_receiver(websocket, client_id))
    try:
        await asyncio.gather(producer, consumer)
    except WebSocketDisconnect:
        pass
    finally:
        query_sessions.pop(client_id, None)
            
    
@api.post('/api/preprocess-query')
async def preprocess_query(request: Request):
    """
    Flask API endpoint for the NaiveRAG system.
    Accepts a POST request with JSON payload containing the user query.
    """
    # Get JSON data from request
    data = await request.json()
    user_query = data.get("query", "")
    if not user_query:
        raise HTTPException(status_code=400, detail="Query not provided")
    
    # Process the user query through NaiveRAG
    # answer = naive_rag.process_query(user_query)
    answer = application.preprocess_query(user_query)
    # return jsonify(answer), 200
    return {"response": answer}
    
@api.post('/api/upload-document')
async def upload_document(file: UploadFile, background_tasks: BackgroundTasks):
    """
    Flask API endpoint to upload a document file.
    """
    # Get the file content
    content = await file.read()
    # Get the file name
    filename = file.filename
    # Check if the file is docx or pdf
    if not filename.endswith((".docx", ".pdf")):
        raise HTTPException(status_code=400, detail="Invalid file format")
    path = os.path.join("uploads", filename)
    async with aiofiles.open(path, "wb+") as f:
        await f.write(content)
    background_tasks.add_task(application.insert_doc, path)
    # Return a 201 response
    return {"message": "Document uploaded successfully"}
    
# Index route, transfer control to the React frontend
# full_path is needed, DO NOT REMOVE
@api.get("/{full_path:path}", response_class=HTMLResponse)
async def index(request: Request, full_path: str):
    entry_path = os.getenv('VITE_ENTRY_PATH', 'src/main.tsx')
    if os.getenv('FLASK_ENV') == 'development':
        return templates.TemplateResponse(
            request=request, name='index-dev.html', context={'entry_path': entry_path}
        )
    else:
    # Production mode
        with open('backend/api/static/dist/.vite/manifest.json') as f:
            manifest = json.load(f)
            entry_stylesheet = 'dist/' + manifest[entry_path]['css'][0]
            entry_script = 'dist/' + manifest[entry_path]['file']
            return templates.TemplateResponse(
                request=request, name='index.html', context={'entry_path': entry_path, 'entry_stylesheet': entry_stylesheet, 'entry_script': entry_script}
            )