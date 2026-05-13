from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from automacao import emitir_relatorio

import threading
import uvicorn


app = FastAPI()

templates = Jinja2Templates(directory='templates')


@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={}
    )


@app.post('/emitir-relatorio')
def emitir():

    thread = threading.Thread(
        target=emitir_relatorio
    )

    thread.start()

    return JSONResponse({
        'mensagem': 'Automação iniciada'
    })


if __name__ == '__main__':

    uvicorn.run(
        'app:app',
        host='0.0.0.0',
        port=5000,
        reload=True
    )