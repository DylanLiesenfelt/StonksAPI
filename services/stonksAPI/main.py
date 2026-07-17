from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from shared.middleware import LoggingMiddleware
from services.stonksAPI.utils.startup import run_startup

from public.root_html import ROOT_HTML
from services.stonksAPI.v1.routers import router as v1_router

async def lifespan(app: FastAPI):
    app.state.http, app.state.ready, app.state.healthy = await run_startup()
    yield
    await app.state.http.close()

app = FastAPI(lifespan=lifespan)
app.add_middleware(LoggingMiddleware)
app.include_router(v1_router)
app.mount("/public", StaticFiles(directory="public"), name="public")


@app.get("/", response_class=HTMLResponse)
async def root():
    return ROOT_HTML


@app.get("/ready")
async def ready():
    if not app.state.ready:
        return JSONResponse(status_code=503, content={"status": "not ready"})
    return {"status": "ok"}


@app.get("/health")
async def health():
    if not app.state.healthy:
        return JSONResponse(status_code=503, content={"status": "not healthy"})
    return {"status": "ok"}