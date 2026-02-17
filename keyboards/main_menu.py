from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.i18n import _

def get_main_menu_kb(lang: str):
    kb = [
        [InlineKeyboardButton(text=_('btn_search', lang), callback_data="menu_search")],
        [
            InlineKeyboardButton(text=_('btn_profile', lang), callback_data="menu_profile"),
            InlineKeyboardButton(text=_('btn_boost', lang), callback_data="menu_boost")
        ],
        [InlineKeyboardButton(text=_('btn_top', lang), callback_data="menu_top")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_search_gender_kb(lang: str):
    kb = [
        [
            InlineKeyboardButton(text=_('targets_male', lang), callback_data="search_male"),
            InlineKeyboardButton(text=_('targets_female', lang), callback_data="search_female")
        ],
        [InlineKeyboardButton(text=_('btn_cancel', lang), callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_search_age_kb(lang: str):
    kb = [
        [
            InlineKeyboardButton(text="18-25", callback_data="age_18_25"),
            InlineKeyboardButton(text="26-35", callback_data="age_26_35")
        ],
        [
            InlineKeyboardButton(text="36+", callback_data="age_36_100"),
            InlineKeyboardButton(text=_('age_all', lang), callback_data="age_14_100")
        ],
        [InlineKeyboardButton(text=_('btn_back', lang), callback_data="menu_search")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
