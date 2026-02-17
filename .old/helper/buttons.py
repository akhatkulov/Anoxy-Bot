from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup,WebAppInfo
from alch import get_channel
def admin_buttons():
    x = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(text="Statistika", callback_data="stat")
    btn2 = InlineKeyboardButton(text="Xabar yuborish", callback_data="send")
    btn3 = InlineKeyboardButton(text="Kanallarni sozlash", callback_data="channels")
    x.add(btn1, btn2, btn3)
    return x


def channel_control():
    x = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(text="➕Kanal qo'shish", callback_data="channel_add")
    btn2 = InlineKeyboardButton(text="➖Kanalni olib tashlash", callback_data="channel_del")
    x.add(btn1, btn2)
    return x

def make_button(cid):
    x = InlineKeyboardMarkup(row_width=1)
    x.add(InlineKeyboardButton("Xabar yuborish", callback_data=f"javob={cid}"))
    return x

def join_key():
    keyboard = InlineKeyboardMarkup(row_width=1)
    x = get_channel()
    r = 1
    for i in x:
        keyboard.add(
            InlineKeyboardButton(f"〽️ {r}-kanal", url=f"https://t.me/{i}")
        )
        r += 1
    keyboard.add(InlineKeyboardButton('✅ Tasdiqlash', callback_data='/start'))
    return keyboard

def send_message():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text="Xabar yuborish", callback_data="Xabar yuborish"))

def home_keys():
    x = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton(text="🔍Qidirish")
    btn2 = KeyboardButton(text="👤Profil")
    btn3 = KeyboardButton(text="📖Qo'llanma")
    x.add(btn1)
    x.add(btn2,btn3)
    return x

def change_buttons():
    x = InlineKeyboardMarkup(row_width=3)
    btn1 = InlineKeyboardButton(text="Ism",callback_data="change_name")
    btn2 = InlineKeyboardButton(text="Rasm",callback_data="change_pic")
    btn3 = InlineKeyboardButton(text="Bio",callback_data="change_bio")
    btn4 = InlineKeyboardButton(text="Kontakt",callback_data="change_contact")
    btn5 = InlineKeyboardButton(text="Yosh",callback_data="change_age")
    x.add(btn1,btn2,btn3)
    x.add(btn4,btn5)
    return x

def main_web_app(cid):
    markup = InlineKeyboardMarkup(row_width=1)
    web_app_info = WebAppInfo(url="https://akhatkulov.github.io")
    button = InlineKeyboardButton(text="Tab", web_app=web_app_info)
    markup.add(button)
    return markup

def choose_gender():
    x = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(text="🧑 Erkak",callback_data="change_gender_to_man")
    btn2 = InlineKeyboardButton(text="👩‍🦰 Ayol",callback_data="change_gender_to_woman")
    x.add(btn1,btn2)
    return x 