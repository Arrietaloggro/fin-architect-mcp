from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {
        "name": "Fin Architect MCP",
        "status": "running",
        "version": "0.1"
    }
