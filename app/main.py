from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
from .agentic_engine import AgenticEngine
from .database import DatabaseManager
import os

app = FastAPI(title="NQL Agent", description="Natural Query Language Agent for PostgreSQL", version="1.0.0")

# Initialize components
db_manager = DatabaseManager()
agentic_engine = AgenticEngine(database_manager=db_manager)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    sql_query: str
    results: List[Dict[str, Any]]
    execution_time: float
    error: str = None
    explanation: str = None
    suggestions: List[str] = []
    response: str = None
    context: Dict[str, Any] = {}
    reasoning_chain: List[Dict[str, Any]] = []
    iteration_count: int = 0
    agent_state: str = "thinking"
    tool_results: Dict[str, Any] = {}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main web interface"""
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/query", response_model=QueryResponse)
async def execute_nql_query(request: QueryRequest):
    """Execute an NQL query and return results with conversational context"""
    try:
        import time
        start_time = time.time()
        
        # Process query with agentic engine (now async with MCP)
        agentic_response = await agentic_engine.process_query(request.query)
        sql_query = agentic_response['sql_query']
        
        # Execute SQL query
        results = db_manager.execute_query(sql_query)
        
        execution_time = time.time() - start_time
        
        return QueryResponse(
            sql_query=sql_query,
            results=results,
            execution_time=execution_time,
            explanation=agentic_response.get('explanation', ''),
            suggestions=agentic_response.get('suggestions', []),
            response=agentic_response.get('response', ''),
            context=agentic_response.get('context', {}),
            reasoning_chain=agentic_response.get('reasoning_chain', []),
            iteration_count=agentic_response.get('iteration_count', 0),
            agent_state=agentic_response.get('agent_state', 'thinking'),
            tool_results=agentic_response.get('tool_results', {})
        )
    except Exception as e:
        return QueryResponse(
            sql_query="",
            results=[],
            execution_time=0.0,
            error=str(e),
            explanation="I encountered an error processing your query.",
            suggestions=["Try rephrasing your question", "Check the database schema", "Ask for help"]
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

@app.get("/api/conversation/history")
async def get_conversation_history():
    """Get conversation history"""
    try:
        history = agentic_engine.get_conversation_history()
        return {"history": history}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/conversation/clear")
async def clear_conversation():
    """Clear conversation context and history"""
    try:
        agentic_engine.clear_context()
        return {"message": "Conversation cleared successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/conversation/context")
async def get_context():
    """Get current conversation context"""
    try:
        context_summary = agentic_engine.get_context_summary()
        return {"context": context_summary}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/mcp/status")
async def get_mcp_status():
    """Get MCP server status and capabilities"""
    try:
        if agentic_engine.mcp_client and agentic_engine.mcp_initialized:
            capabilities = await agentic_engine.mcp_client.discover_capabilities()
            return {
                "status": "connected",
                "mcp_enabled": True,
                "capabilities": capabilities,
                "server_type": "CrystalDBA Postgres MCP Pro"
            }
        else:
            return {
                "status": "disconnected",
                "mcp_enabled": False,
                "message": "Real MCP server not initialized",
                "server_type": "CrystalDBA Postgres MCP Pro"
            }
    except Exception as e:
        return {"error": str(e), "mcp_enabled": False}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
