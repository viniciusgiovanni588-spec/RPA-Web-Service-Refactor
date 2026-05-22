from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response

from core.database import supabase

router = APIRouter()
templates = Jinja2Templates(directory='frontend/templates')

# rota de signup
@router.get('/cadastro', response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='register.html',
        context={}
    )

@router.post('/cadastro')
async def signup_login(full_name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    try:
        auth_response = supabase.auth.sign_up({
            'email': email,
            'password': password,
            'options': {
                'data': {
                    'full_name': full_name
                }
            }
        })
        if auth_response.user is None:
            raise HTTPException(status_code=400, detail='Signup failed')
        
        supabase.table('user_table').insert({
            'full_name': full_name,
            'email': email,
            'auth_user_id': password
        }).execute()
        
        return RedirectResponse('/login', status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get('/login', response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='login.html',
        context={}
    )

@router.post('/login', response_class=HTMLResponse)
async def login_auth(response: Response, email: str = Form(...), password: str = Form(...)):
    try:
        auth_response = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        if auth_response.user is None:
            raise HTTPException(status_code=400, detail='Login failed')
        access_token = auth_response.session.access_token
        response = RedirectResponse('/dashboard', status_code=303)
        response.set_cookie(key='access_token', value=f'Bearer {access_token}', httponly=True)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/logout')
async def logout(response: Response):
    response = RedirectResponse('/login', status_code=303)
    response.delete_cookie(key='access_token')
    return response