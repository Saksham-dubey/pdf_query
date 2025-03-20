from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from workflows.jobs.pdf_processor import PDFProcessor
from workflows.utils.utils import list_pdf_files
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize PDF processor with your PDF files
pdf_processor = PDFProcessor(api_key=os.getenv('OPENAI_API_KEY'))
# Assuming you have a list of PDF paths
pdf_directory = os.path.join(os.getcwd(), "PDF")
PDF_PATHS = list_pdf_files(pdf_directory) # Update this with your PDF paths
pdf_processor.upload_pdfs(PDF_PATHS)

class QueryRequest(BaseModel):
    query: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/process-query")
async def process_query(query_request: QueryRequest):
    if not query_request.query:
        raise HTTPException(status_code=400, detail="No query provided")
    
    try:
        response = pdf_processor.process_query(query_request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cleanup")
async def cleanup():
    try:
        pdf_processor.cleanup_files()
        return {"message": "Cleanup successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    finally:
        # Clean up files when the application shuts down
        pdf_processor.cleanup_files() 
