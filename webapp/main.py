from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import AsyncSessionLocal
from bot.utils.security import verify_admin_token

app = FastAPI(title="Vapeshop Admin")

templates = Jinja2Templates(directory="webapp/templates")
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

def require_admin(token: str) -> int:
    try:
        payload = verify_admin_token(token)
        return int(payload["tg_id"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "token": token
    })
