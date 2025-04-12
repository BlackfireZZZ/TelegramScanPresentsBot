from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from src.gifts import parse_members
from src.database import Database
from config import ADMINS
from src.data.keyboards import get_mode_keyboard, get_level_keyboard


router = Router()
IS_ACTIVE = False


@router.message(CommandStart())
async def start_handler(message: Message):
    if not Database.admin_exists(message.from_user.id):
        return await message.answer('<b>❌ Вы не являетесь администратором</b>')
    
    await message.answer(
        text='<b>⚡️ Отправьте чаты списком и парсинг пользователей начнется автоматически</b>'
    )


@router.message(Command("stop"))
async def stop_handler(message: Message):
    if not Database.admin_exists(message.from_user.id):
        return await message.answer('<b>❌ Вы не являетесь администратором</b>')
    if not Database.get_user_is_parser(message.from_user.id):
        return await message.answer('<b>❌ Нет активного парсинга</b>')
    
    Database.update_user_is_parser(message.from_user.id, False)
    await message.answer('<b>✅ Парсинг остановлен</b>')

@router.message(Command("settings"))
async def settings_handler(message: Message):
    if not Database.admin_exists(message.from_user.id):
        return await message.answer('<b>❌ Вы не являетесь администратором</b>')
    
    current_mode = Database.get_user_mode(message.from_user.id)
    current_level = Database.get_user_level(message.from_user.id)
    
    text = (
        "<b>Настройки парсера</b>\n\n"
        f"Текущий режим: {'Рекурсивный' if current_mode == 2 else 'Обычный'}\n"
        f"Уровень рекурсии: {current_level}\n\n"
        "Доступные команды:\n"
        "/mode - Изменить режим парсинга\n"
        "/level - Установить уровень рекурсии"
    )
    
    await message.answer(text)


@router.message(Command("mode"))
async def mode_handler(message: Message):
    if not Database.admin_exists(message.from_user.id):
        return await message.answer('<b>❌ Вы не являетесь администратором</b>')
    
    await message.answer(
        "<b>Выберите режим парсинга:</b>\n\n"
        "Обычный - парсинг только указанных чатов\n"
        "Рекурсивный - парсинг с отслеживанием источников подарков",
        reply_markup=get_mode_keyboard()
    )


@router.message(Command("level"))
async def level_handler(message: Message):
    if not Database.admin_exists(message.from_user.id):
        return await message.answer('<b>❌ Вы не являетесь администратором</b>')
    
    await message.answer(
        "<b>Выберите уровень рекурсии:</b>\n\n"
        "Уровень определяет глубину поиска источников подарков",
        reply_markup=get_level_keyboard()
    )


@router.callback_query(lambda c: c.data.startswith(("mode_", "level_")))
async def process_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if not Database.admin_exists(user_id):
        return await callback.answer("❌ Вы не являетесь администратором")
    
    action, value = callback.data.split("_")
    value = int(value)
    
    if action == "mode":
        Database.update_user_mode(user_id, value)
        mode_text = "Рекурсивный" if value == 2 else "Обычный"
        await callback.message.edit_text(f"<b>✅ Установлен {mode_text} режим парсинга</b>")
    else:
        Database.update_user_level(user_id, value)
        await callback.message.edit_text(f"<b>✅ Установлен {value} уровень рекурсии</b>")
    
    await callback.answer()

@router.message(F.from_user.id.in_(ADMINS))
async def chats_handler(message: Message):
    if Database.get_user_is_parser(message.from_user.id):
        return await message.answer('<b>❌ Дождитесь окончания предыдущего парсинга</b>')
    
    Database.update_user_is_parser(message.from_user.id, True)

    chats = message.text.split('\n')
    for index, chat in enumerate(chats):
        chats[index] = chat.replace('https://', '').replace('t.me/', '').replace('@', '')

    result_message = await message.answer(f'<b>📑 Начали парсинг {len(chats)} чатов.</b>')

    for chat in chats:
        async for result_gift, user_id, username in parse_members(message.bot.user_session, message.from_user.id, chat):
            sorted_gifts = sorted(result_gift, key=lambda x: x["level"])
            
            result_text = f'<b>🌟 Чат: @{chat} | Юзер: @{username} [id: {user_id}]</b>\n'
            gifts_text = ""

            current_level = 0
            for item in sorted_gifts:
                if item["level"] != current_level:
                    current_level = item["level"]
                    gifts_text += f'\n<b>Уровень {current_level}:</b>\n'

                gift_line = f'<b><i>•</i></b> Gift: {item["gift"]} - <b>{item["name"]}</b> (@{item["username"]})\n'
                
                if len(result_text + gifts_text + gift_line) <= 4096:
                    gifts_text += gift_line
                else:
                    break 
                    
            await result_message.reply(result_text + gifts_text)

    await result_message.reply('<b>✅ Парсинг окончен</b>')
    Database.update_user_is_parser(message.from_user.id, False)