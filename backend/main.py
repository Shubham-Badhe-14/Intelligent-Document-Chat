from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import uuid
import uvicorn
from contextlib import asynccontextmanager

from document_processor import extract_text, chunk_text
from llm_client import get_embedding, get_query_embedding, generate_answer
from vector_store import VectorStore

# Initialize Vector Store
vector_store = VectorStore(dimension=768)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create uploads directory
    os.makedirs("uploads", exist_ok=True)
    yield
    # Shutdown: Clean up if needed

app = FastAPI(lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development convenience
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    document_id: str
    question: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        # Generate a document ID
        doc_id = str(uuid.uuid4())
        file_path = f"uploads/{doc_id}_{file.filename}"
        
        # Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Read file content for processing
        with open(file_path, "rb") as f:
            content = f.read()
            
        # Extract Text
        text = extract_text(content, file.filename)
        if not text:
             raise HTTPException(status_code=400, detail="Could not extract text from file.")

        # Chunk Text
        chunks = chunk_text(text)
        if not chunks:
             raise HTTPException(status_code=400, detail="Document appears empty after text extraction.")
             
        # Generate Embeddings
        # Note: In a real app, we might want to batch this.
        embeddings = []
        for chunk in chunks:
            emb = get_embedding(chunk)
            embeddings.append(emb)
            
        # Add to Vector Store
        # We clear the existing store for MVP simplicity (one doc at a time focus) 
        # as per "Answers change appropriately when a different document is uploaded".
        # But instructions say "keyed by document_id". 
        # The user interaction implies uploading A, getting ID A, querying A.
        # Uploading B, getting ID B, querying B.
        # So we should strictly probably NOT clear, but just filter by ID if we could.
        # However, FAISS IndexFlatL2 doesn't support metadata filtering natively.
        # For this MVP, let's keep it simple: The VectorStore stores ALL chunks.
        # But wait, if I query, I want to query *that* document.
        # The prompt says: "Embeddings are indexed... When unique user asks... retrieve... chunks".
        # It doesn't explicitly strict filtering, but it's implied "User uploads PDF... ask question about THAT document".
        # If I upload 2 docs, and ask about Doc A, I shouldn't get chunks from Doc B.
        # Since I'm using a simple FAISS index without metadata filtering, I have a few options:
        # 1. One index per document (in memory dict).
        # 2. Re-implement VectorStore to support ID filtering (brute force or separate indices).
        # Given "MVP", let's use a dictionary of VectorStores or just one retrieval and post-filtering ?
        # Post-filtering is hard if the index returns top K globally.
        # Let's simple create a new VectorStore for each document or session?
        # Actually, "Store in memory, keyed by a generated document_id" implies we might want to store the whole structure.
        
        # DECISION: To keep it robust yet MVP:
        # I will modify VectorStore to support multiple documents via a trick or just simple dict of indices?
        # Actually, `vector_store.py` has `doc_map`. But `search` doesn't filter.
        # Let's simple CLEAR the vector store on new upload for this "Single User / Single Document Focus" MVP flow unless user wants multi-doc.
        # Requirement: "Answers change appropriately when a different document is uploaded."
        # Requirement: "Store in memory, keyed by a generated document_id"
        # Let's update VectorStore to be a dictionary of indices? Or just one global index?
        # If I have global index, and I upload Doc A (physics) and Doc B (cooking).
        # I query Doc B. FAISS might return Doc A chunks if they are semantically similar? Unlikely if topics differ.
        # But to be safe, filtering is best.
        # Let's adjust `main.py` to use a global dictionary `sessions = {doc_id: VectorStore()}`?
        # Yes, that's safest for "keyed by document_id".
        
        # Re-reading requirements: "Store in memory, keyed by a generated document_id"
        # This hints that the DATA itself or the Index should be keyed.
        
        # Let's just instantiate a new VectorStore for each upload and store in a global dict.
        
        global document_limits
        # Simple in-memory storage for MVP
        if not hasattr(app.state, "vector_stores"):
            app.state.vector_stores = {}
            
        # Create a fresh store for this document
        # This ensures strict isolation.
        doc_store = VectorStore(dimension=768)
        doc_store.add_documents(doc_id, chunks, embeddings)
        app.state.vector_stores[doc_id] = doc_store
        
        return {"document_id": doc_id, "message": "File processed successfully", "chunks": len(chunks)}

    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_document(request: QueryRequest):
    if not hasattr(app.state, "vector_stores") or request.document_id not in app.state.vector_stores:
         raise HTTPException(status_code=404, detail="Document not found. Please upload first.")
         
    store = app.state.vector_stores[request.document_id]
    
    try:
        # Embed Question
        query_emb = get_query_embedding(request.question)
        
        # Retrieve Context
        context_chunks = store.search(query_emb, k=5)
        
        # Generate Answer
        answer = generate_answer(request.question, context_chunks)
        
        return {
            "answer": answer,
            "sources": context_chunks
        }
    except Exception as e:
        print(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{document_id}/content")
async def get_document_content(document_id: str):
    # Find the file in uploads directory
    # Since we prefix with doc_id, we can find it.
    # filename pattern: {doc_id}_{filename}
    
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        raise HTTPException(status_code=404, detail="Uploads directory not found")
        
    files = os.listdir(upload_dir)
    target_file = None
    for f in files:
        if f.startswith(document_id + "_"):
            target_file = f
            break
            
    if not target_file:
         raise HTTPException(status_code=404, detail="Document file not found")
         
    file_path = os.path.join(upload_dir, target_file)
    from fastapi.responses import FileResponse
    # Force inline display and correct mime type
    return FileResponse(file_path, media_type="application/pdf", headers={"Content-Disposition": "inline"})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
