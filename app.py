import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from alch import User, create_user, get_cid2, put_cid2, get_step, put_step, put_arg, get_arg, user_count, get_all_user, \
    get_channel, put_channel, get_channel_with_id, delete_channel

bot = telebot.TeleBot('7024076459:AAGRYZpsRgOugWFY7Bu28tK7CRWIFGF8UVc', parse_mode="html")


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


admin_id = 6521895096


def mini_crypt(a: str) -> str:
    l = {'0': 'a', '1': 'x', '2': 'p', '3': 't', '4': 's', '5': 'l', '6': 'r', '7': 'f', '8': 'u', '9': 'e'}
    res = ""
    for char in a:
        res += l[char]
    return res


def mini_decrypt(a: str) -> str:
    l = {'a': '0', 'x': '1', 'p': '2', 't': '3', 's': '4', 'l': '5', 'r': '6', 'f': '7', 'u': '8', 'e': '9'}
    res = ""
    for char in a:
        res += l[char]
    return res


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


def join(user_id):
    try:
        xx = get_channel()
        r = 0
        for i in xx:
            res = bot.get_chat_member(f"@{i}", user_id)
            x = ['member', 'creator', 'administrator']
            if res.status in x:
                r += 1
        if r != len(xx):
            bot.send_message(user_id,
                             "<b>👋 Assalomu alaykum Botni ishga tushurish uchun kanallarga a'zo bo'ling va a'zolikni tekshirish buyrug'ini bosing.</b>",
                             parse_mode='html', reply_markup=join_key())
            return False
        else:
            return True
    except Exception as e:
        bot.send_message(chat_id=admin_id, text=f"Kanalga bot admin qilinmagan yoki xato: {str(e)}")
        return True


def make_button(cid):
    x = InlineKeyboardMarkup(row_width=1)
    x.add(InlineKeyboardButton("Xabar yuborish", callback_data=f"javob={cid}"))
    return x


def send_message():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text="Xabar yuborish", callback_data="Xabar yuborish"))


@bot.message_handler(commands=['start'])
def start(message):
    try:
        create_user(cid=message.chat.id)
    except Exception as e:
        print(f"Error creating user: {str(e)}")

    if message.text == "/start" and join(message.chat.id):
        put_step(cid=message.chat.id, step="!!!")
        status = get_cid2(message.chat.id)
        if status == 0:
            bot.send_message(message.chat.id,
                             f"Salom sizda sherik yo'q\nTaklif linki:\nhttps://t.me/Anoxy_Bot?start={mini_crypt(str(message.chat.id))}",
                             parse_mode='html')
        else:
            bot.send_message(message.chat.id,
                             f'Sizda hamroh bor xabar yuborish uchun "Xabar yuborish" tugmasini bosing\nTaklif linki:\nhttps://t.me/Anoxy_Bot?start={mini_crypt(str(message.chat.id))}',
                             parse_mode='html', reply_markup=send_message())

    if "/start" in message.text and len(message.text) > 6:
        adder = list(message.text.split())
        x = adder[1]
        res = mini_decrypt(x)
        put_step(cid=message.chat.id, step="!!!")
        put_cid2(cid=message.chat.id, cid2=int(res))
        bot.send_message(message.chat.id, 'Sizda hamroh bor xabar yuborish uchun "Xabar yuborish" tugmasini bosing',
                         reply_markup=send_message())


@bot.message_handler(content_types=['text'])
def more(message):
    if message.text == '/link' and join(message.chat.id):
        bot.send_message(message.chat.id,
                         f"\nTaklif linki:\nhttps://t.me/Anoxy_Bot?start={mini_crypt(str(message.chat.id))}",
                         parse_mode='html')
    if message.text == "/admin" and message.chat.id == admin_id:
        bot.send_message(chat_id=admin_id, text="Salom, Admin", reply_markup=admin_buttons())
        put_step(cid=message.chat.id, step="!!!")

    if get_step(message.chat.id) == "channel_del" and message.text != "/start" and message.text != "/admin":
        x = int(message.text)
        if delete_channel(ch_id=x):
            bot.send_message(chat_id=message.chat.id, text="Kanal olib tashlandi")
            put_step(cid=message.chat.id, step="!!!")
        else:
            bot.send_message(chat_id=message.chat.id, text="Xatolik! IDni to'g'ri kiritdingizmi tekshiring!")

    if get_step(message.chat.id) == "add_channel" and message.text != "/start" and message.text != "/admin":
        if put_channel(message.text):
            bot.send_message(chat_id=message.chat.id, text=f"{message.text} kanali qabul qilindi!")
            put_step(cid=int(admin_id), step="!!!")
        else:
            bot.send_message(chat_id=message.chat.id,
                             text="Xatolik! Bu kanal oldin qo'shilgan bo'lishi mumkin yoki boshqa xatolik, iltimos tekshiring")
            put_step(cid=int(admin_id), step="!!!")
    if get_step(message.chat.id) == 'send':
        text = message.text
        mid = message.id
        bot.send_message(chat_id=message.chat.id, text="Xabar yuborish boshlandi")
        try:
            for i in get_all_user():
                try:
                    bot.forward_message(chat_id=i, from_chat_id=admin_id, message_id=mid)
                except Exception as e:
                    print(f"Error sending message to user {i}: {str(e)}")
            bot.send_message(chat_id=message.chat.id, text="Tarqatish yakunlandi")
            put_step(cid=int(admin_id), step="!!!")
        except Exception as e:
            bot.send_message(chat_id=message.chat.id, text=f"Xabar yuborishda muammo bo'ldi: {str(e)}")
    if message.text == "/stat" and message.chat.id == admin_id:
        bot.send_message(chat_id=message.chat.id, text=f"Foydalanuvchilar soni: {user_count()}")
    if message.text == "/send" and message.chat.id == admin_id:
        bot.send_message(chat_id=message.chat.id, text="Forward xabaringizni yuboring")
        put_step(cid=message.chat.id, step="send")
    if get_step(int(message.chat.id)) == '1' and join(message.chat.id):
        x = message.chat.id
        bot.send_message(get_arg(message.chat.id),
                         f"Yangi xabar keldi!<b>\n{message.text}\n</b>Javob yozish uchun tugmani bosing!",
                         reply_markup=make_button(x))
        bot.send_message(message.chat.id, "Xabaringiz foydalanuvchiga yuborildi!")
        put_step(message.chat.id, '0')
    if get_step(message.chat.id) == '3' and join(message.chat.id):
        bot.send_message(chat_id=message.chat.id, text="Xabaringiz yuborildi!")
        x = message.chat.id
        bot.send_message(chat_id=get_cid2(message.chat.id), text=f"Sizda yangi xabar bor: <b>{message.text} </b>",
                         reply_markup=make_button(x))
        put_step(message.chat.id, '0')


@bot.message_handler(content_types=['document', 'gif', 'video', 'photo', 'audio', 'voice'])
def for_admin(message):
    if get_step(int(message.chat.id)) == '1' and join(message.chat.id):
        z = message.chat.id
        bot.send_message(chat_id=z, text="Xabaringiz foydalanuvchiga yuborildi!")
        x = bot.copy_message(get_arg(message.chat.id), message.chat.id, message.id,
                             caption=f"📨 Sizga yangi anonim xabar bor: <b>{message.caption}</b>",
                             reply_markup=make_button(z))
        bot.send_message(chat_id=get_arg(z), text="...", reply_to_message_id=x.message_id, reply_markup=make_button(z))
        put_step(message.chat.id, '0')
    if get_step(message.chat.id) == '3' and join(message.chat.id):
        bot.send_message(chat_id=message.chat.id, text="Xabaringiz yuborildi!")
        z = message.chat.id
        x = bot.copy_message(get_cid2(message.chat.id), message.chat.id, message.id,
                             caption=f"📨 Sizga yangi anonim xabar bor: <b>{message.caption}</b>")
        bot.send_message(chat_id=get_cid2(z), text="...", reply_to_message_id=x.message_id, reply_markup=make_button(z))
        put_step(message.chat.id, '0')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "/start" and join(call.message.chat.id):
        status = get_cid2(call.message.chat.id)
        if status == 0:
            bot.send_message(call.message.chat.id, f"Salom sizda sherik yo'q\nTaklif linki:\nhttps://t.me/Anoxy_Bot?start={mini_crypt(str(call.message.chat.id))}")
        else:
            bot.send_message(call.message.chat.id,
                             f'Sizda hamroh bor xabar yuborish uchun "Xabar yuborish" tugmasini bosing\nTaklif linki:\nhttps://t.me/Anoxy_Bot?start={mini_crypt(str(call.message.chat.id))}',
                             reply_markup=send_message())

    if call.data == "Xabar yuborish" and join(call.message.chat.id):
        bot.send_message(call.message.chat.id, "Xabaringizni yuboring")
        put_step(call.message.chat.id, '3')
    if call.data.startswith("javob=") and join(call.message.chat.id):
        put_step(call.message.chat.id, '1')
        put_arg(call.message.chat.id, call.data.split("=")[1])
        bot.send_message(call.message.chat.id, "Xabaringizni kiriting:")
    if call.data == "stat" and str(call.message.chat.id) == str(admin_id):
        bot.send_message(chat_id=call.message.chat.id, text=f"Foydalanuvchilar soni: {user_count()}")
    if call.data == "send" and str(call.message.chat.id) == str(admin_id):
        put_step(cid=call.message.chat.id, step="send")
        bot.send_message(chat_id=call.message.chat.id, text="Forward xabaringizni yuboring")
    if call.data == "channels" and str(call.message.chat.id) == str(admin_id):
        r = get_channel_with_id()
        bot.send_message(chat_id=call.message.chat.id, text=f"Kanallar ro'yxati:{r}", reply_markup=channel_control())
    if call.data == "channel_add" and str(call.message.chat.id) == str(admin_id):
        put_step(cid=call.message.chat.id, step="add_channel")
        bot.send_message(chat_id=call.message.chat.id, text="Kanali linkini yuboring! bekor qilish uchun /start !")
    if call.data == "channel_del" and str(call.message.chat.id) == str(admin_id):
        put_step(cid=call.message.chat.id, step="channel_del")
        bot.send_message(chat_id=call.message.chat.id,
                         text=f"{get_channel_with_id()}\nO'chirmoqchi bo'lgan kanalingiz IDsini bering, bekor qilish uchun /start yoki /admin deng!")


if __name__ == '__main__':
    print(bot.get_me())
    bot.polling(none_stop=True)
