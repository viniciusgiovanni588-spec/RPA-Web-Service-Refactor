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
        normalized_email = email.strip().lower()
        normalized_name = full_name.strip()

        auth_response = supabase.auth.sign_up({
            'email': normalized_email,
            'password': password,
            'options': {
                'data': {
                    'full_name': normalized_name
                }
            }
        })
        if auth_response.user is None:
            raise HTTPException(status_code=400, detail='Signup failed')
        
        supabase.table('user_table').insert({
            'full_name': normalized_name,
            'email': normalized_email,
            'auth_user_id': auth_response.user.id
        }).execute()
        
        return RedirectResponse('/login', status_code=303)
    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=400,
                            detail='Email inválido. Verifique se o endereço está completo e sem espaços extras.')
    

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