import telebot
from photolink import PhotoLink
from io import BytesIO

from alch import User, create_user, get_cid2, put_cid2, get_step, put_step, put_arg, get_arg, user_count, get_all_user, \
    get_channel, put_channel, get_channel_with_id, delete_channel,get_info,check_user,change_info

from helper.buttons import admin_buttons,channel_control,make_button,send_message,join_key, home_keys,change_buttons,main_web_app
from helper.functions import mini_decrypt, mini_crypt, is_number

import conf

bot = telebot.TeleBot(conf.BOT_TOKEN, parse_mode="html")


admin_id = conf.ADMIN_ID
photolink = PhotoLink()


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
                             f"<b>Salom, {message.chat.first_name} botimizga xush kelibsiz</b>",
                             parse_mode='html',reply_markup=home_keys())
        else:
            bot.send_message(message.chat.id,
                             f'❗️Xabar yuborish uchun <b>"Xabar yuborish"</b> tugmasini bosing\n\n🔗Taklif linki:\nhttps://t.me/Anoxy_Bot?start={mini_crypt(str(message.chat.id))}',
                             parse_mode='html', reply_markup=send_message())

    if "/start" in message.text and len(message.text) > 6:
        adder = list(message.text.split())
        x = adder[1]
        res = mini_decrypt(x)
        put_step(cid=message.chat.id, step="!!!")
        put_cid2(cid=message.chat.id, cid2=int(res))
        bot.send_message(message.chat.id, '❗️Xabar yuborish uchun <b>"Xabar yuborish"</b> tugmasini bosing',
                         reply_markup=send_message())


@bot.message_handler(content_types=['text'])
def more(message):
    if message.text == "🔍Qidirish":
        if check_user(cid=message.chat.id):
            bot.send_message(chat_id=message.chat.id,text="👇👇👇",reply_markup=main_web_app(cid=message.chat.id))
        else:
            bot.send_message(chat_id=message.chat.id,text="Profilni yetarlicha to'ldirmagansiz!!!")
    
    if message.text == "👤Profil":
        user_info = get_info(cid=message.chat.id)
        res = f"<b>Rasm:</b><a href='{user_info['pic']}'>LINK</a>\n<b>Ism:</b> {user_info["name"]}\n<b>Bio:</b> {user_info["info"]}\n<b>Yosh:</b> {user_info["age"]}\n<b>Kontakt:</b> {user_info["contact"]}\n\n<b>Savol-Javob uchun havola👇</b>\nhttps://t.me/Anoxy_Bot?start={mini_crypt(str(message.chat.id))}\n\n<b>Agarda ma'lumotlaringizdan birini o'zgartirmoqchi bo'lsangiz👇</b>"
        bot.send_message(chat_id=message.chat.id,text=res,parse_mode="html",reply_markup=change_buttons())
    
    if message.text == "📖Qo'llanma":
        bot.send_message(chat_id=message.chat.id,text="Tez kunda...")
    
    if message.text == '/link' and join(message.chat.id):
        bot.send_message(message.chat.id,
                         f"\n🔗Taklif linki:\nhttps://t.me/Anoxy_Bot?start={mini_crypt(str(message.chat.id))}",
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
        put_cid2(cid=message.chat.id, cid2=0)
    
    if get_step(message.chat.id) == '3' and join(message.chat.id):
        bot.send_message(chat_id=message.chat.id, text="Xabaringiz yuborildi!")
        x = message.chat.id
        bot.send_message(chat_id=get_cid2(message.chat.id), text=f"Sizda yangi xabar bor: <b>{message.text} </b>",
                         reply_markup=make_button(x))
        put_step(message.chat.id, '0')
        put_cid2(cid=message.chat.id, cid2=0)
    
    if get_step(message.chat.id) == "change_name":
        if len(message.text) < 75:
            change_info(cid=message.chat.id,type_info="name",value=message.text)
            bot.send_message(chat_id=message.chat.id,text=f"Ismingiz <b>{message.text}</b>ga o'zgartirildi✅",parse_mode="html")
            put_step(message.chat.id, '0')
        else:
            bot.send_message(cid=message.chat.id,text="Xatolik! Ism haddan tashqari uzun. Qaytadan yuboring:")

    if get_step(message.chat.id) == "change_bio":
        change_info(cid=message.chat.id,type_info="info",value=message.text)
        bot.send_message(chat_id=message.chat.id,text="O'zgartirildi✅")
        put_step(message.chat.id, '0')

    if get_step(message.chat.id) == "change_contact":
        change_info(cid=message.chat.id,type_info="contact",value=message.text)
        bot.send_message(chat_id=message.chat.id,text="O'zgartirildi✅")
        put_step(message.chat.id, '0')
    
    if get_step(message.chat.id) == "change_age":
        if is_number(message.text):
            change_info(cid=message.chat.id,type_info="age",value=int(message.text))
            bot.send_message(chat_id=message.chat.id,text="O'zgartirildi✅")
            put_step(message.chat.id, '0')           
        else:
            bot.send_message(chat_id=message.chat.id,text="Xatolik! Menga raqam yuboring!")
    

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
        put_cid2(cid=message.chat.id, cid2=0)
    if get_step(message.chat.id) == '3' and join(message.chat.id):
        bot.send_message(chat_id=message.chat.id, text="Xabaringiz yuborildi!")
        z = message.chat.id
        x = bot.copy_message(get_cid2(message.chat.id), message.chat.id, message.id,
                             caption=f"📨 Sizga yangi anonim xabar bor: <b>{message.caption}</b>")
        bot.send_message(chat_id=get_cid2(z), text="...", reply_to_message_id=x.message_id, reply_markup=make_button(z))
        put_step(message.chat.id, '0')
        put_cid2(cid=message.chat.id, cid2=0)
    if get_step(message.chat.id) =="change_pic":
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_stream = BytesIO(downloaded_file)
        file_stream.name = 'temp.jpg' 

        try:
            upload = photolink.upload_image(file_path=file_stream)
            bot.reply_to(message, f"<a href='{upload}'>O'zgartirildi✅</a>",parse_mode="html")
            change_info(cid=message.chat.id,type_info="pic",value=telegraph_url)
        except Exception as e:
            bot.reply_to(message, f"Xato: {e}")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "/start" and join(call.message.chat.id):
        status = get_cid2(call.message.chat.id)
        if status == 0:
            bot.send_message(call.message.chat.id, f"""<b>🔗Bu sizning shaxsiy havolangiz: </b>

https://t.me/Anoxy_Bot?start={mini_crypt(str(call.message.chat.id))}

<b>♻️Ulashish orqali anonim suhbat quring!</b>""")
        else:
            bot.send_message(call.message.chat.id,
                             f'❗️Xabar yuborish uchun "Xabar yuborish" tugmasini bosing\n\n🔗Taklif linki:\nhttps://t.me/Anoxy_Bot?start={mini_crypt(str(call.message.chat.id))}',
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
                         text=f"{get_channel_with_id()}\n⚠️O'chirmoqchi bo'lgan kanalingiz IDsini bering, bekor qilish uchun /start yoki /admin deng!")

    if call.data == "change_gender":
        bot.send_message(chat_id=message.chat.id,text="Tanlang:",reply_markup=choose_gender())
    if call.data == "change_name":
        put_step(cid=call.message.chat.id,step="change_name")
        bot.send_message(chat_id=call.message.chat.id,text="✍️Ismingizni yuboring:")
    if call.data == "change_bio":
        put_step(cid=call.message.chat.id,step="change_bio")
        bot.send_message(chat_id=call.message.chat.id,text="Yangi ma'lumotlarni yuboring")
    if call.data == "change_contact":
        put_step(cid=call.message.chat.id,step="change_contact")
        bot.send_message(chat_id=call.message.chat.id,text="Siz bilan bog'lanish uchun yangi kontaktlarni bering")
    if call.data == "change_age":
        put_step(cid=call.message.chat.id,step="change_age")
        bot.send_message(chat_id=call.message.chat.id,text="Yoshingizni yuboring")
    if call.data == "change_pic":
        put_step(cid=call.message.chat.id,step="change_pic")
        bot.send_message(chat_id=call.message.chat.id,text="1 dona rasm yuboring!")

    if call.data == "change_gender_to_man":
        put_arg(cid=call.message.chat.id,type_info="gender",value="erkak")
        bot.send_message(chat_id=call.message.chat.id,text="Bajarildi✅")
    if call.data == "change_gender_to_woman":
        put_arg(cid=call.message.chat.id,type_info="gender",value="ayol")
        bot.send_message(chat_id=call.message.chat.id,text="Bajarildi✅")




if __name__ == '__main__':
    print(bot.get_me())
    bot.polling(none_stop=True)
