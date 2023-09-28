from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from  .routers import registration, monitor
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(registration.router, prefix="/registration", tags=["registration"])
app.include_router(monitor.router, prefix="/monitor", tags=["monitor"])

@app.get("/")
async def root():
    return {"message": "Server is running"}