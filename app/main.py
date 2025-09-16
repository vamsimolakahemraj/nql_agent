from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
from .nql_engine import NQLEngine
from .database import DatabaseManager
import os

app = FastAPI(title="NQL Agent", description="Natural Query Language Agent for PostgreSQL", version="1.0.0")

# Initialize components
nql_engine = NQLEngine()
db_manager = DatabaseManager()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    sql_query: str
    results: List[Dict[str, Any]]
    execution_time: float
    error: str = None

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main web interface"""
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/query", response_model=QueryResponse)
async def execute_nql_query(request: QueryRequest):
    """Execute an NQL query and return results"""
    try:
        import time
        start_time = time.time()
        
        # Convert NQL to SQL
        sql_query = nql_engine.nql_to_sql(request.query)
        
        # Execute SQL query
        results = db_manager.execute_query(sql_query)
        
        execution_time = time.time() - start_time
        
        return QueryResponse(
            sql_query=sql_query,
            results=results,
            execution_time=execution_time
        )
    except Exception as e:
        return QueryResponse(
            sql_query="",
            results=[],
            execution_time=0.0,
            error=str(e)
        )

@app.get("/api/schema")
async def get_database_schema():
    """Get database schema information"""
    try:
        schema = db_manager.get_schema()
        return {"schema": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        db_manager.test_connection()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
