from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from shared.middleware import LoggingMiddleware
from shared.error_handler import register_exception_handlers
from services.indexes.utils.startup import run_startup

async def lifespan(app: FastAPI):
    app.state.http, app.state.ready, app.state.healthy = await run_startup()
    yield
    await app.state.http.close()

app = FastAPI(lifespan=lifespan)
app.add_middleware(LoggingMiddleware)
register_exception_handlers(app)
#app.include_router()


@app.get("/", response_class=HTMLResponse)
async def root():
    return {
        "message" : "Indexes Service"
    }


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