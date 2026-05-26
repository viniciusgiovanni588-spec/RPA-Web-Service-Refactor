from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.middleware import AdvancedMiddleware
from app.auth import auth_routes
from app.routes import routes

app = FastAPI()

# Mount the static files directory
app.mount('/static', StaticFiles(directory='frontend/static'), name='static')

# Set up templates
templates = Jinja2Templates(directory='frontend/templates')

# include middleware
app.add_middleware(AdvancedMiddleware)

# include routers
app.include_router(routes.router)
app.include_router(auth_routes.router)