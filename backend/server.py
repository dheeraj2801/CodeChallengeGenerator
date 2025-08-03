from src.app import app

if __name__ == "__main__":
    import uvicorn
    
    import logging

    logging.basicConfig(
        level=logging.DEBUG,  # Use INFO or WARNING for production
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    uvicorn.run(app, host="0.0.0.0", port=8000)