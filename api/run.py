import uvicorn
import os
import logging

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get host and port from environment variables or use defaults
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    
    # Log message before starting the server
    print(f"Starting API server at http://{host}:{port}")
    
    # Run the uvicorn server
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True  # Enable auto-reload during development
    ) 