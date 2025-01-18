import os
from typing import Union

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware

try:
    from deck import FrameDeck
    from base import CardInfoOfficial
except:
    from src.deck import FrameDeck
    from src.base import CardInfoOfficial

app = FastAPI()

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (substitua por uma lista específica para maior segurança)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# Configuração para a pasta de templates
temp = os.path.join(os.path.dirname(__file__), 'templates')
templates = Jinja2Templates(directory=temp)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", {
            "request": request,
            "message": "Aviso importante!"
    })

@app.get("/decklist")
def read_item(ydke: Union[str, None] = None):
    if ydke:
        ydke = ydke.strip()
        ydke = ydke.replace(' ', '+').replace('/decklist?ydke=', '')
        core = FrameDeck(ydke)
        dados = core.get_dict_deck()
        return JSONResponse(dados)
    else:
        return JSONResponse('Parameter ydke= not insered', status_code=400)

@app.get('/card')
def read_card(id: str):
    if id:
        id = int(id)
        card = CardInfoOfficial(id)
        return JSONResponse(card.info_card)
    return JSONResponse('Parameter "id" not insered', status_code=400)

if __name__ == '__main__':
    uvicorn.run(uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True))
