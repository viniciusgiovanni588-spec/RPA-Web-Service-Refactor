from fastapi import APIRouter, Request, Form, HTTPException
from pydantic import EmailStr, ValidationError, TypeAdapter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response

from core.database import supabase

router = APIRouter()
templates = Jinja2Templates(directory='frontend/templates')

# rota de signup
@router.get('/cadastro', response_class=HTMLResponse)
async def signup(request: Request):
    """
    Renderiza a página de cadastro de usuário
    Args:
        request (Request): Requisição HTTP do FastAPI.
    Returns:
        HTMLResponse: página register.html renderizada.
    """
    return templates.TemplateResponse(
        request=request,
        name='register.html',
        context={}
    )

@router.post('/cadastro')
async def signup_login(full_name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    """
    Cria um novo usuário no sistema via Supabase Auth e salva dados adicionais.

    Fluxo:
    1. Normaliza email e nome
    2. Valida formato do email localmente
    3. Cria usuário no Supabase Auth
    4. Salva dados complementares na tabela user_Table
    5. Redireciona para login

    Args:
        full_name (str): nome completo do usuário
        email (str): email do usuário
        password (str): senha do usuário

    Returns:
        RedirectResponse: redireciona para página de login
    
    Raises:
        HTTPException:
            - 400: email inválido
            - 400: falha no signup
            - 400: erro retornado pelo Supabase
    """

    normalized_email = email.strip().lower()
    normalized_name = full_name.strip()

    try:
        # Validação local para retornar feedback mais claro antes de chamar o banco de dados.
        normalized_email = TypeAdapter(EmailStr).validate_python(normalized_email)
    except ValidationError:
        raise HTTPException(
            status_code=400,
            detail='Email inválido. Verifique se o endereço está completo e sem espaços extras.'
        )
    
    try:
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
            'id': auth_response.user.id
        }).execute()
        
        return RedirectResponse('/login', status_code=303)
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        lowered_error = error_message.lower()

        if 'email' in lowered_error and ('invalid' in lowered_error):
            raise HTTPException(
                status_code=400,
                detail='Email inválido. Verifique se o endereço esta completo e sem espaços extras.'
            )
        
        raise HTTPException(status_code=400, detail=error_message)
    

@router.get('/login', response_class=HTMLResponse)
async def login(request: Request):
    """
    Renderiza a página de login.

    Args:
        request (Request): requisição HTTP.

    Returns:
        HTMLResponse: página login.html renderizada.
    """
    return templates.TemplateResponse(
        request=request,
        name='login.html',
        context={}
    )

@router.post('/login', response_class=HTMLResponse)
async def login_auth(response: Response, email: str = Form(...), password: str = Form(...)):
    """
    Autentica o usuário e cria sessão via cookie JWT.

    Fluxo:
        1. Normaliza email
        2. Valida formato do email
        3. Autentica no Supabase
        4. Gera session token
        5. Armazena token em cookie HttpOnly
        6. Redireciona para dashboard

    Args:
        response (Response): resposta HTTP (FastAPI)
        email (str): email do usuário
        password (str): senha do usuário

    Returns:
        RedirectResponse: redireciona para index

    Raises:
        HTTPException:
            - 400: email inválido
            - 400: falha no login
    """
    normalized_email = email.strip().lower()

    try:
        # Validação local para retornar feedback mais claro antes de chamar o banco de dados.
        normalized_email = TypeAdapter(EmailStr).validate_python(normalized_email)
    except ValidationError:
        raise HTTPException(
            status_code=400,
            detail='Email inválido. Verifique se o endereço está completo e sem espaços extras.'
        )
    
    try:
        auth_response = supabase.auth.sign_in_with_password({
            'email': normalized_email,
            'password': password
        })
        if auth_response.user is None:
            raise HTTPException(status_code=400, detail='Login failed')
        access_token = auth_response.session.access_token
        response = RedirectResponse('/', status_code=303)
        response.set_cookie(key='access_token', value=access_token, httponly=True, secure=False, samesite='lax', path='/')
        return response
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/logout')
async def logout(response: Response):
    """
    Remove o cookie de autenticação e encerra a sessão.

    Returns:
        RedirectResponse: redireciona para login.
    """
    response = RedirectResponse('/', status_code=303)
    response.delete_cookie(key='access_token')
    return response