from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_mode_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="Обычный режим", callback_data="mode_1"),
            InlineKeyboardButton(text="Рекурсивный режим", callback_data="mode_2")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_level_keyboard() -> InlineKeyboardMarkup:
    keyboard = []
    row = []
    
    for i in range(1, 6):
        row.append(InlineKeyboardButton(text=str(i), callback_data=f"level_{i}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
        
    return InlineKeyboardMarkup(inline_keyboard=keyboard)