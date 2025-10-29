import bcrypt
from datetime import datetime, timedelta, timezone
import jwt
from configuration.settings import settings

def hash_password(p: str) -> str:
    return bcrypt.hashpw(p.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def check_password(p: str, h: str) -> bool:
    return bcrypt.checkpw(p.encode("utf-8"), h.encode("utf-8"))

def make_admin_token(tg_id: int) -> str:
    exp_min = int(getattr(settings, "ADMIN_JWT_EXPIRES_MIN", 120))
    payload = {"tg_id": tg_id, "exp": datetime.now(timezone.utc) + timedelta(minutes=exp_min)}
    return jwt.encode(payload, settings.ADMIN_JWT_SECRET, algorithm="HS256")

def verify_admin_token(token: str) -> dict:
    return jwt.decode(token, settings.ADMIN_JWT_SECRET, algorithms=["HS256"])
