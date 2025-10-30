from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from entities.models import User, RegistrationRequest, City
from bot.utils.security import hash_password

router = Router()


class RegistrationStates(StatesGroup):
    waiting_for_password = State()
    waiting_for_password_confirm = State()
    waiting_for_city = State()


@router.message(Command("register"))
async def cmd_register(message: Message, state: FSMContext, session: AsyncSession):
    # Перевірка чи користувач вже зареєстрований
    result = await session.execute(
        select(User).where(User.tg_id == message.from_user.id)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        await message.answer("Ви вже зареєстровані в системі!")
        return
    
    # Перевірка чи є заявка на реєстрацію
    result = await session.execute(
        select(RegistrationRequest).where(
            RegistrationRequest.tg_id == message.from_user.id,
            RegistrationRequest.status == "pending"
        )
    )
    existing_request = result.scalar_one_or_none()
    
    if existing_request:
        await message.answer("Ваша заявка на реєстрацію вже в обробці. Зачекайте підтвердження адміністратора.")
        return
    
    username = message.from_user.username or f"user_{message.from_user.id}"
    
    await message.answer(
        f"📝 <b>Реєстрація в системі</b>\n\n"
        f"В якості логіна буде використаний ваш username: <code>@{username}</code>\n\n"
        f"Введіть пароль (мінімум 6 символів):",
        reply_markup=ReplyKeyboardRemove()
    )
    
    await state.update_data(username=username)
    await state.set_state(RegistrationStates.waiting_for_password)


@router.message(RegistrationStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text
    
    # Видаляємо повідомлення з паролем для безпеки
    try:
        await message.delete()
    except:
        pass
    
    if len(password) < 6:
        await message.answer("❌ Пароль має містити мінімум 6 символів. Спробуйте ще раз:")
        return
    
    await state.update_data(password=password)
    await message.answer("🔐 Повторіть пароль для підтвердження:")
    await state.set_state(RegistrationStates.waiting_for_password_confirm)


@router.message(RegistrationStates.waiting_for_password_confirm)
async def process_password_confirm(message: Message, state: FSMContext, session: AsyncSession):
    password_confirm = message.text
    
    # Видаляємо повідомлення з паролем для безпеки
    try:
        await message.delete()
    except:
        pass
    
    data = await state.get_data()
    password = data.get("password")
    
    if password != password_confirm:
        await message.answer("❌ Паролі не співпадають. Введіть пароль ще раз:")
        await state.set_state(RegistrationStates.waiting_for_password)
        return
    
    # Отримуємо список міст
    result = await session.execute(
        select(City).where(City.is_active == True)
    )
    cities = result.scalars().all()
    
    if not cities:
        await message.answer("❌ На жаль, наразі немає доступних міст. Зверніться до адміністратора.")
        await state.clear()
        return
    
    # Створюємо клавіатуру з містами
    keyboard_buttons = []
    row = []
    for city in cities:
        row.append(KeyboardButton(text=city.name))
        if len(row) == 2:
            keyboard_buttons.append(row)
            row = []
    if row:
        keyboard_buttons.append(row)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "🏙️ Виберіть ваше місто:",
        reply_markup=keyboard
    )
    await state.set_state(RegistrationStates.waiting_for_city)


@router.message(RegistrationStates.waiting_for_city)
async def process_city(message: Message, state: FSMContext, session: AsyncSession):
    city_name = message.text
    
    # Перевіряємо чи існує місто
    result = await session.execute(
        select(City).where(City.name == city_name, City.is_active == True)
    )
    city = result.scalar_one_or_none()
    
    if not city:
        await message.answer("❌ Таке місто не знайдено. Виберіть місто з клавіатури.")
        return
    
    data = await state.get_data()
    username = data.get("username")
    password = data.get("password")
    
    # Хешуємо пароль
    password_hash = hash_password(password)
    
    # Створюємо заявку на реєстрацію
    registration_request = RegistrationRequest(
        tg_id=message.from_user.id,
        username=username,
        password_hash=password_hash,
        city_id=city.id,
        status="pending"
    )
    
    session.add(registration_request)
    await session.commit()
    
    await message.answer(
        "✅ <b>Ваша заявка на реєстрацію відправлена!</b>\n\n"
        f"Місто: <b>{city.name}</b>\n"
        f"Username: <code>@{username}</code>\n\n"
        "⏳ Очікуйте підтвердження адміністратора.",
        reply_markup=ReplyKeyboardRemove()
    )
    
    await state.clear()
