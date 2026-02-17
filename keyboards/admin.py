from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_main_kb():
    kb = [
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
            InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton(text="🔍 Foydalanuvchini qidirish", callback_data="admin_search"),
            InlineKeyboardButton(text="⚠️ Shikoyatlar", callback_data="admin_reports")
        ],
        [
            InlineKeyboardButton(text="❌ Yopish", callback_data="admin_close")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_admin_cancel_kb():
    kb = [[InlineKeyboardButton(text="🚫 Bekor qilish", callback_data="admin_main")]]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_admin_user_kb(user_id: int, is_banned: bool):
    ban_text = "🔓 Bandan yechish" if is_banned else "🚫 Bloklash"
    kb = [
        [InlineKeyboardButton(text="🔥 Boost berish (+50)", callback_data=f"adm_boost_{user_id}")],
        [InlineKeyboardButton(text=ban_text, callback_data=f"adm_ban_{user_id}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
