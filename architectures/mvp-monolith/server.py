#!/usr/bin/env python3
"""
Combined server for Brand Creator
Serves both the frontend and API
"""

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from api.main import app as api_app

# Create the main app
app = FastAPI(
    title="Brand Creator Full Stack",
    description="AI-powered brand creation platform",
    version="1.0.0"
)

# Mount the API
app.mount("/api", api_app)

# Mount static files for frontend
frontend_path = os.path.join(project_root, "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the main frontend page"""
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            return {"message": "Frontend not found"}
    
    @app.get("/{path:path}")
    async def serve_frontend_files(path: str):
        """Serve frontend files"""
        file_path = os.path.join(frontend_path, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        else:
            # Return index.html for client-side routing
            index_path = os.path.join(frontend_path, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
            else:
                return {"error": "File not found"}
else:
    @app.get("/")
    async def no_frontend():
        return {
            "message": "Brand Creator API",
            "frontend": "Frontend not found",
            "api_docs": "/docs",
            "health": "/api/health"
        }

if __name__ == "__main__":
    print("Starting Brand Creator server...")
    print("Frontend: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print("Health check: http://localhost:8000/api/health")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
