from fastapi import APIRouter, Request, Depends, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.auth.auth_middleware import get_current_user
from core.forms import as_form
from core.database import supabase, SUPABASE_URL, SUPABASE_KEY

router = APIRouter()
templates = Jinja2Templates(directory='frontend/templates')

# Rota index
@router.get('/', response_class=HTMLResponse)
async def index(request: Request):
    """
    Renderiza a página de index

    Args:
        request (Request): requisição HTTP.
    Returns:
        HTMLReponse: página index.html renderizada.
    """
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={}
    )

# Rota Dashboard
@router.get('/dashboard', response_class=HTMLResponse)
async def dashboard(request: Request,
                    current_user: dict = Depends(get_current_user)):
    """
    Renderiza a página de dashboard
    """
    return templates.TemplateResponse(
        name="dashboard.html",
        request=request,
        context={
            'user_email': current_user['email']
            }
    )
