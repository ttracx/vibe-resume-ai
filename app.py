# HuggingFace Spaces compatibility
from main import app

# For HuggingFace Spaces, use this file name
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
