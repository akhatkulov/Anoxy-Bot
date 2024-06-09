import telebot
from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup

from alch import User,create_user,get_cid2,put_cid2,get_step,put_step,put_arg,get_arg,user_count,get_all_user,get_channel,put_channel

bot = telebot.TeleBot('5899601127:AAGWIjpikVaUOuyNuqre1N3NvCnZJ--QEp8',parse_mode="html")


def admin_buttons():
    x = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(text="Statistika",callback_data="stat")
    btn2 = InlineKeyboardButton(text="Xabar yuborish",callback_data="send")
    btn3 = InlineKeyboardButton(text="Kanallarni sozlash",callback_data="channels")
    x.add(btn1,btn2,btn3)
    return x

def channel_control():
    x = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(text="➕Kanal qo'shish",callback_data="channel_add")
    btn2 = InlineKeyboardButton(text="➖Kanalni olib tashlash",callback_data="channel_del")
    x.add(btn1,btn2)
    return x


admin_id = 6521895096

def join_key():
    keyboard = InlineKeyboardMarkup(row_width=1)
  
    x = get_channel()
    r = 1
    for i in x:
        keyboard.add(
            InlineKeyboardButton(f"〽️ {r}-kanal",url=f"https://t.me/{i}")
        )
    r+=1
  

    keyboard.add(InlineKeyboardButton('✅ Tasdiqlash', callback_data='/start'))
    return keyboard
def join(user_id):
    xx = get_channel()
    r = 0
    for i in xx:
        res = bot.get_chat_member(f"@{i}", user_id)
        x = ['member', 'creator', 'administrator']
        if res.status in x:
            r+=1
    if r!=len(xx):
        bot.send_message(user_id,"<b>👋 Assalomu alaykum Botni ishga tushurish uchun kanallarga a'zo bo'ling va a'zolikni tekshirish buyrug'ini bosing.</b>",parse_mode='html',reply_markup=join_key())
        return False
    else:
        return True



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
    if message.text=="/start" and join(message.chat.id):
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
    if message.text == "/admin" and message.chat.id == admin_id:
        bot.send_message(chat_id=admin_id,text="Salom, Admin",reply_markup=admin_buttons())
    if get_step(message.chat.id) == "add_channel" and message.text != "/start" and message.text != "/admin":
        if put_channel(message.text):
            bot.send_message(chat_id=message.chat.id,text=f"{message.text} kanali qabul qilindi!")
            put_step(cid=int(admin_id),step="!!!")
        else:
            bot.send_message(chat_id=message.chat.id,text="Xatolik! Bu kanal oldin qo'shilgan bolishi mumkin yoki boshqa xatolik, iltimos tekshiring")
            put_step(cid=int(admin_id),step="!!!")
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
            put_step(cid=int(admin_id),step="!!!")
        except:
            bot.send_message(chat_id=message.chat.id,text="Xabar yuborishda muammo bo'ldi")
    if message.text == "/stat" and message.chat.id == admin_id:
        bot.send_message(chat_id=message.chat.id,text=f"Foydalanuvchilar soni: {user_count()}")
    if message.text == "/send" and message.chat.id == admin_id:
        bot.send_message(chat_id=message.chat.id,text="Forward xabaringizni yuboring")
        put_step(cid=message.chat.id,step="send")
    if get_step(int(message.chat.id)) == '1' and join(message.chat.id):
        x = message.chat.id
        bot.send_message(get_arg(message.chat.id),f"Yangi xabar keldi!<b>\n{message.text}\n</b>Javob yozish uchun tugmani bosing!",reply_markup=make_button(x))
        bot.send_message(message.chat.id, "Xabaringiz foydalanuvchiga yuborildi!")
        put_step(message.chat.id,'0')
    if get_step(message.chat.id)=='3' and join(message.chat.id):
        bot.send_message(chat_id=message.chat.id, text="Xabaringiz yuborildi!")
        x = message.chat.id
        bot.send_message(chat_id=get_cid2(message.chat.id),text=f"Sizda yangi xabar bor: <b>{message.text} </b>",reply_markup=make_button(x))
        put_step(message.chat.id,'0')

@bot.message_handler(content_types=['document','gif','video','photo','audio','voice'])
def for_admin(message):
    print(">>>>>>>")
    print(message.chat.id)
    if get_step(int(message.chat.id))=='1' and join(message.chat.id):

        z = message.chat.id
        bot.send_message(chat_id=z, text="Xabaringiz foydalanuvchiga yuborildi!")
        x = bot.copy_message(get_arg(message.chat.id), message.chat.id, message.id,
                         caption=f"📨 Sizga yangi anonim xabar bor: <b>{message.caption}</b>",
                         reply_markup=make_button(z))
        bot.send_message(chat_id=get_arg(z),text="...",reply_to_message_id=x.message_id,reply_markup=make_button(z))

        put_step(message.chat.id,'0')
    if get_step(message.chat.id)=='3' and join(message.chat.id):
        bot.send_message(chat_id=message.chat.id, text="Xabaringiz yuborildi!")
        z = message.chat.id
        x = bot.copy_message(get_cid2(message.chat.id), message.chat.id, message.id, caption=f"📨 Sizga yangi anonim xabar bor: <b>{message.caption}</b>")
        bot.send_message(chat_id=get_cid2(z),text="...",reply_to_message_id=x.message_id,reply_markup=make_button(z))
        put_step(message.chat.id,'0')

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if join(call.message.chat.id):

        status = get_cid2(call.message.chat.id)
        if status == 0:
            bot.send_message(call.message.chat.id,"Salom sizda sherik yo'q")
        else:
            bot.send_message(call.message.chat.id, 'Sizda hamroh bor xabar yuborish uchun "Xabar yuborish" tugmasini bosing',reply_markup=send_message())
    
    if call.data == "Xabar yuborish" and join(call.message.chat.id):
        bot.send_message(call.message.chat.id,"Xabaringizni yuboring")
        put_step(call.message.chat.id,'3')
    if call.data.startswith("javob=") and join(call.message.chat.id):
        put_step(call.message.chat.id,'1')
        put_arg(call.message.chat.id,call.data.split("=")[1])
        bot.send_message(call.message.chat.id, "Xabaringizni kiriting:")
    if call.data == "stat"  and str(call.message.chat.id) == str(admin_id):
        bot.send_message(chat_id=call.message.chat.id,text=f"Foydalanuvchilar soni: {user_count()}")
    if call.data == "send" and str(call.message.chat.id) == str(admin_id):
        put_step(cid=call.message.chat.id, step="send")
        bot.send_message(chat_id=call.message.chat.id,text="Forward xabaringizni yuboring")
    if call.data == "channels" and str(call.message.chat.id) == str(admin_id):
        bot.send_message(chat_id=call.message.chat.id,text=f"Kanallar ro'yxati:{[1,2,3]}",reply_markup=channel_control())
    if call.data == "channel_add" and str(call.message.chat.id)==str(admin_id):
        put_step(cid=call.message.chat.id,step="add_channel")
        bot.send_message(chat_id=call.message.chat.id,text="Kanali linkini yuboring! bekor qilish uchun /start !")



if __name__ == '__main__':
    print(bot.get_me())
    bot.polling(none_stop=True)
