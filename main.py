from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/hello")
async def hello_world():
    return {"message": "Hello, World!"}
