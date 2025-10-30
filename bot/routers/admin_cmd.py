from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from entities.models import Admin
from bot.utils.security import check_password, make_admin_token
from configuration.settings import settings

router = Router(name="admin_cmd_router")

@router.message(Command("admin"))
async def admin_enter(message: Message, session: AsyncSession):
    res = await session.execute(
        select(Admin).where(Admin.tg_id == message.from_user.id, Admin.is_active == True)
    )
    adm = res.scalar_one_or_none()
    if not adm:
        return
    
    parts = message.text.strip().split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "🔐 <b>Вхід до адмін-панелі</b>\n\n"
            "Введіть пароль у форматі:\n"
            "<code>/admin ваш_пароль</code>"
        )
        return

    password = parts[1]

    if not check_password(password, adm.password_hash):
        await message.answer("🚫 Невірний пароль.")
        return

    token = make_admin_token(message.from_user.id)
    url = f"{settings.ADMIN_PANEL_URL}?token={token}"
    
    await message.answer(
        f"✅ <b>Доступ дозволено!</b>\n\n"
        f"🌐 <b>Відкрийте адмін-панель:</b>\n"
        f'<a href="{url}">🔗 Vapeshop Admin Panel</a>\n\n'
        f"⏱️ Токен дійсний протягом 2 годин\n"
        f"🔒 Посилання персональне та захищене",
        parse_mode="HTML",
        disable_web_page_preview=False
    )
