import telebot
from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup

from alch import User,create_user,get_cid2,put_cid2,get_step,put_step,put_arg,get_arg,user_count,get_all_user

bot = telebot.TeleBot('5899601127:AAGWIjpikVaUOuyNuqre1N3NvCnZJ--QEp8')


admin_id = 6521895096
print("------------")
get_step(6521895096)
print("------------")

def admin_buttons():
    x = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(text="Statistika",callback_data="stat")
    btn2 = InlineKeyboardButton(text="Xabar yuborish",callback_data="send")
    btn3 = InlineKeyboardButton(text="Kanallarni sozlash",callback_data="channel")
    x.add(btn1,btn2,btn3)
    return x
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
    if message.text == "/start" and message.chat.id == admin_id:
        bot.send_message(chat_id=admin_id,text="Salom, Admin",reply_markup=admin_buttons())
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

def handle_message(message):
    # if get_step(message.chat.id) == 'send':
    #     text = message.text
    #     mid = message.id
    #     bot.send_message(chat_id = message.chat.id,text="xabar yuborish boshlandi")
    #     bot.send_message(chat_id = message.chat.id,text=str(get_all_user()))
    #
    #     try:
    #         for i in get_all_user():
    #             try:
    #                 print(i)
    #                 bot.forward_message(chat_id=i,from_chat_id=admin_id,message_id=mid)
    #             except:
    #                 print("error send message to groups")
    #         bot.send_message(chat_id=message.chat.id,text="tarqatish yakunlandi")
    #     except:
    #         bot.send_message(chat_id=message.chat.id,text="Xabar yuborishda muammo bo'ldi")
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
    if call.data == "stat"  and str(call.message.chat.id) == str(admin_id):
        bot.send_message(chat_id=call.message.chat.id,text=f"Foydalanuvchilar soni: {user_count()}")
    if call.data == "send" and call.message.chat.id == admin_id:
        put_step(cid=call.message.chat.id, step="send")
        bot.send_message(chat_id=call.message.chat.id,text="Forward xabaringizni yuboring")

    if call.data == "Xabar yuborish":
        bot.send_message(call.message.chat.id,"Xabaringizni yuboring")
        put_step(call.message.chat.id,'3')
    if call.data.startswith("javob="):
        put_step(call.message.chat.id,'1')
        put_arg(call.message.chat.id,call.data.split("=")[1])
        bot.send_message(call.message.chat.id, "Xabaringizni kiriting:")


if __name__ == '__main__':
    bot.polling(none_stop=True)
