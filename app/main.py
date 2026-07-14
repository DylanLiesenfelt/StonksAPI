from fastapi import FastAPI

from public.root_html import ROOT_HTML

app = FastAPI()

@app.get("/")
async def root():
    return ROOT_HTML