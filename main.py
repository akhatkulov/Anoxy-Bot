import telebot
from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup

from alch import User,create_user,get_cid2,put_cid2,get_step,put_step,put_arg,get_arg,user_count,get_all_user

bot = telebot.TeleBot('5899601127:AAGWIjpikVaUOuyNuqre1N3NvCnZJ--QEp8')


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
       # put_cid2(cid=adder[1],cid2=message.chat.id)
        bot.send_message(message.chat.id, 'Sizda hamroh bor xabar yuborish uchun "Xabar yuborish" tugmasini bosing',reply_markup=send_message())
        # put_step(message.chat.id,'3')

@bot.message_handler()
def for_admin(message):
    if get_step(message.chat.id) and message.chat.id == admin_id:
        text = message.text
        try:
            for i in get_all_user():
                bot.copy_message(chat_id=i, from_chat_id=message.chat.id,message_id=message.message_id, caption=message.caption)
            bot.send_message(chat_id=message.chat.id,text="tarqatish yakunlandi")
        except:
            bot.send_message(chat_id=message.chat.id,text="Xabar yuborishda muammo bo'ldi")
    if message.text == "/stat"  and message.chat.id == admin_id:
        bot.send_message(chat_id=message.chat.id,text=f"Foydalanuvchilar soni: {user_count()}")
    if message.text == "/send" and message.chat.id == admin_id:
        bot.send_message(chat_id=message.chat.id,text="Forward axabringizni yuboring")
        put_step(cid=message.chat.id,step="send")




def handle_message(message):
    if get_step(int(message.chat.id))=='1':
        x = message.chat.id
        bot.send_message(get_arg(message.chat.id),f"Yangi xabar keldi!\n{message.text}\nJavob yozish uchun tugmani bosing!",reply_markup=make_button(x))
        bot.send_message(message.chat.id, "Xabaringiz foydalanuvchiga yuborildi!")
        put_step(message.chat.id,'0')
    if get_step(message.chat.id)=='3':
        bot.send_message(chat_id=message.chat.id, text="Xabaringiz yuborildi!")
        x = message.chat.id
        bot.send_message(get_cid2(message.chat.id), f"Yangi xabar keldi!\n{message.text}\nJavob yozish uchun tugmani bosing!",reply_markup=make_button(x))

        put_step(message.chat.id,'0')

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "Xabar yuborish":
        bot.send_message(call.message.chat.id,"Xabaringizni yuboring")
        put_step(call.message.chat.id,'3')
    if call.data.startswith("javob="):
        put_step(call.message.chat.id,'1')
        put_arg(call.message.chat.id,call.data.split("=")[1])
        bot.send_message(call.message.chat.id, "Xabaringizni kiriting:")


if __name__ == '__main__':
    bot.polling(none_stop=True)
