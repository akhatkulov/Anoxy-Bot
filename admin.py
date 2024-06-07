import telebot
from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup

bot = telebot.TeleBot('5899601127:AAGWIjpikVaUOuyNuqre1N3NvCnZJ--QEp8')
admin_id = 6521895096
from alch import get_step,get_all_user,user_count,put_step,put_channel,get_channel

def admin_buttons():
    x = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(text="Statistika",callback_data="stat")
    btn2 = InlineKeyboardButton(text="Xabar yuborish",callback_data="send")
    btn3 = InlineKeyboardButton(text="Kanallarni sozlash",callback_data="channel")
    x.add(btn1,btn2,btn3)
    return x

def channel_control():
    x = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(text="➕Kanal qo'shish",callback_data="channel_add")
    btn2 = InlineKeyboardButton(text="➖Kanalni olib tashlash",callback_data="channel_del")



@bot.message_handler()
def admin(message):
    if message.text == "/admin" and message.chat.id == admin_id:
        bot.send_message(chat_id=admin_id,text="Salom, Admin",reply_markup=admin_buttons())
    if get_step(message.chat.id) == "channel_add" and message.text != "/start":
        if put_channel(message.text):
            bot.send_message(chat_id=message.chat.id,text=f"{message.text} kanali qabul qilindi!")
        else:
            bot.send_message(chat_id=message.chat.id,text="Xatolik! Bu kanal oldin qo'shilgan bolishi mumkin yoki boshqa xatolik, iltimos tekshiring")
    if get_step(message.chat.id) == 'send':
        text = message.text
        mid = message.id
        bot.send_message(chat_id = message.chat.id,text="xabar yuborish boshlandi")
        bot.send_message(chat_id = message.chat.id,text=str(get_all_user()))
    
        try:
            for i in get_all_user():
                try:
                    print(i)
                    bot.forward_message(chat_id=i,from_chat_id=admin_id,message_id=mid)
                except:
                    print("error send message to groups")
            bot.send_message(chat_id=message.chat.id,text="tarqatish yakunlandi")
        except:
            bot.send_message(chat_id=message.chat.id,text="Xabar yuborishda muammo bo'ldi")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "stat"  and str(call.message.chat.id) == str(admin_id):
        bot.send_message(chat_id=call.message.chat.id,text=f"Foydalanuvchilar soni: {user_count()}")
    if call.data == "send" and str(call.message.chat.id) == admin_id:
        put_step(cid=call.message.chat.id, step="send")
        bot.send_message(chat_id=call.message.chat.id,text="Forward xabaringizni yuboring")
    if call.data == "send" and str(call.message.chat.id) == str(admin_id):
        bot.send_message(chat_id=call.message.chat.id,text=f"Tanishing kanllar ro'yxati:{[1,2,3]}",reply_markup=channel_control())
    if call.data == "channel_add" and str(call.message.chat.id)==str(admin_id):
        put_step(cid=call.message.chat.id,step="add_channel")
        bot.send_message(chat_id=call.message.chat.id,text="Kanali linkini yuboring! bekor qilish uchun /start !")

bot.polling()