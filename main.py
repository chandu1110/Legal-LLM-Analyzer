from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .models import LegalAnalyzer

# Create an instance of the FastAPI application
app = FastAPI(
    title="Legal Document Analysis API",
    description="An API that uses open-source LLMs to analyze legal text.",
    version="1.0.0"
)

# Initialize the analyzer. This loads the models into memory and happens only once at startup.
try:
    analyzer = LegalAnalyzer()
except Exception as e:
    # If model loading fails, the server should not start correctly.
    raise RuntimeError(f"Failed to initialize LegalAnalyzer: {e}")


# Define the data model for the incoming request body
class Document(BaseModel):
    text: str
    class Config:
        schema_extra = {
            "example": {
                "text": "This Agreement is made between Party A and Party B. "
                        "The term of this agreement is for five years. "
                        "Party A shall not be liable for any breach of contract..."
            }
        }


@app.get("/", tags=["General"])
def read_root():
    """ A welcome message to verify the API is running. """
    return {"message": "Welcome to the Legal LLM Analysis API. Go to /docs for documentation."}


@app.post("/analyze", tags=["Analysis"])
def analyze_document(doc: Document):
    """
    Analyzes a legal document to perform risk assessment, summarization, and clause extraction.
    """
    if not doc.text or not doc.text.strip():
        raise HTTPException(status_code=400, detail="Document text cannot be empty.")
    
    try:
        print("\n[API] Received request. Starting analysis...")

        # 1. Perform risk analysis
        print("[API] Analyzing risk...")
        risk = analyzer.analyze_risk(doc.text)
        print(f"[API] Risk assessment complete: {risk}")

        # 2. Extract clauses and entities
        print("[API] Extracting clauses...")
        clauses = analyzer.extract_clauses(doc.text)
        print(f"[API] Clause extraction complete. Found {len(clauses)} entities.")
        
        # 3. Generate summary
        print("[API] Generating summary...")
        summary = analyzer.summarize_document(doc.text)
        print("[API] Summary generation complete.")

        print("[API] Analysis finished. Returning results.")
        
        return {
            "summary": summary,
            "risk_assessment": risk,
            "extracted_clauses": clauses,
        }

    except Exception as e:
        # A general catch-all for any unexpected errors during analysis
        print(f"[API] An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))