import telebot
from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup

from alch import User,create_user,get_cid2,put_cid2,get_step,put_step,put_arg,get_arg,user_count,get_all_user

bot = telebot.TeleBot('5899601127:AAGWIjpikVaUOuyNuqre1N3NvCnZJ--QEp8',parse_mode="html")


admin_id = '6521895096'

def make_button(cid):
    x = InlineKeyboardMarkup(row_width=1)
    x.add(InlineKeyboardButton("Xabar yuborish",callback_data=f"javob={cid}"))
    return x
def send_message():
    return InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text="Xabar yuborish",callback_data="Xabar yuborish"))

@bot.message_handler(commands=['start'])
def start(message):
    try:
        create_user(cid=message.chat.id)
    except:
        print("member error")
    if message.text=="/start":
        status = get_cid2(message.chat.id)
        if status == 0:
            bot.send_message(message.chat.id,"Salom sizda sherik yo'q")
        else:
            bot.send_message(message.chat.id, 'Sizda hamroh bor xabar yuborish uchun "Xabar yuborish" tugmasini bosing',reply_markup=send_message())

    if len(message.text)>6:
        adder = list(message.text.split())
        put_cid2(cid=message.chat.id,cid2=adder[1])
        bot.send_message(message.chat.id, 'Sizda hamroh bor xabar yuborish uchun "Xabar yuborish" tugmasini bosing',reply_markup=send_message())

@bot.message_handler(content_types=['text'])
def more(message):
    if message.text == "/stat" and message.chat.id == admin_id:
        bot.send_message(chat_id=message.chat.id,text=f"Foydalanuvchilar soni: {user_count()}")
    if message.text == "/send" and message.chat.id == admin_id:
        bot.send_message(chat_id=message.chat.id,text="Forward xabaringizni yuboring")
        put_step(cid=message.chat.id,step="send")
    if get_step(int(message.chat.id)) == '1':
        x = message.chat.id
        bot.send_message(get_arg(message.chat.id),f"Yangi xabar keldi!<b>\n{message.text}\n</b>Javob yozish uchun tugmani bosing!",reply_markup=make_button(x))
        bot.send_message(message.chat.id, "Xabaringiz foydalanuvchiga yuborildi!")
        put_step(message.chat.id,'0')
    if get_step(message.chat.id)=='3':
        bot.send_message(chat_id=message.chat.id, text="Xabaringiz yuborildi!")
        x = message.chat.id
        bot.send_message(chat_id=get_cid2(message.chat.id),text=f"Sizda yangi xabar bor: <b>{message.text} </b>",reply_markup=make_button(x))
        put_step(message.chat.id,'0')

@bot.message_handler(content_types=['document','gif','video','photo','audio','voice'])
def for_admin(message):
    print(">>>>>>>")
    print(message.chat.id)
    if get_step(int(message.chat.id))=='1':

        z = message.chat.id
        bot.send_message(chat_id=z, text="Xabaringiz foydalanuvchiga yuborildi!")
        x = bot.copy_message(get_arg(message.chat.id), message.chat.id, message.id,
                         caption=f"📨 Sizga yangi anonim xabar bor: <b>{message.caption}</b>",
                         reply_markup=make_button(z))
        bot.send_message(chat_id=get_arg(z),text="...",reply_to_message_id=x.message_id,reply_markup=make_button(z))

        put_step(message.chat.id,'0')
    if get_step(message.chat.id)=='3':
        bot.send_message(chat_id=message.chat.id, text="Xabaringiz yuborildi!")
        z = message.chat.id
        x = bot.copy_message(get_cid2(message.chat.id), message.chat.id, message.id, caption=f"📨 Sizga yangi anonim xabar bor: <b>{message.caption}</b>")
        bot.send_message(chat_id=get_cid2(z),text="...",reply_to_message_id=x.message_id,reply_markup=make_button(z))
        put_step(message.chat.id,'0')

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    print(call.data)
    print(call)
    if call.data == "Xabar yuborish":
        bot.send_message(call.message.chat.id,"Xabaringizni yuboring")
        put_step(call.message.chat.id,'3')
    if call.data.startswith("javob="):
        put_step(call.message.chat.id,'1')
        put_arg(call.message.chat.id,call.data.split("=")[1])
        bot.send_message(call.message.chat.id, "Xabaringizni kiriting:")


if __name__ == '__main__':
    print(bot.get_me())
    bot.polling(none_stop=True)
