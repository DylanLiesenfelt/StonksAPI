from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from shared.client import Client

from public.root_html import ROOT_HTML
from services.stonksAPI.v1.routers import router as v1_router

async def lifespan(app: FastAPI):
    app.state.http = Client()
    yield
    await app.state.http.close()

app = FastAPI(lifespan=lifespan)
app.include_router(v1_router)
app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/", response_class=HTMLResponse)
async def root():
    return ROOT_HTML