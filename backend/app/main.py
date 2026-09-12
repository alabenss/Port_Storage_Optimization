from fastapi import FastAPI


app = FastAPI(
    title="Port Storage Optimization System",
    description="Automatic port cargo storage management and optimization",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Port Storage Optimization API is running"
    }