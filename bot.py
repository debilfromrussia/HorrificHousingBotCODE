import telebot
from telebot import types
import threading

# ================= НАСТРОЙКИ =================
TOKEN = "8405287668:AAFGC1qUVhItxcMhffJcNafSN5lCXMisyrY"

OWNERS = [
    1941490846,   # ← твой ID
    1480732438    # ← второй ID (потом замени)
]

HASHTAG = "\n\n#тейк ⊹ ˖✮⋆˙ @HorrificHousingBOT"
# ============================================

bot = telebot.TeleBot(TOKEN)

media_groups = {}

def send_to_all_owners(media_list=None, text=None, photo=None, video=None, caption=None):
    for owner_id in OWNERS:
        try:
            if media_list:
                bot.send_media_group(owner_id, media_list)
            elif photo:
                bot.send_photo(owner_id, photo, caption=caption)
            elif video:
                bot.send_video(owner_id, video, caption=caption)
            elif text:
                bot.send_message(owner_id, text)
        except:
            pass


def process_album(media_group_id):
    if media_group_id not in media_groups:
        return
    group = media_groups.pop(media_group_id)
    messages = group['messages']
    user_chat_id = group['user_chat_id']

    if not messages:
        return

    media = []
    for i, msg in enumerate(messages):
        caption = (msg.caption or "") + HASHTAG if i == 0 else None
        if msg.photo:
            media.append(types.InputMediaPhoto(msg.photo[-1].file_id, caption=caption))
        elif msg.video:
            media.append(types.InputMediaVideo(msg.video.file_id, caption=caption))

    if media:
        send_to_all_owners(media_list=media)

    bot.send_message(user_chat_id, "✅ Ваш тейк отправлен!")


# ====================== ОБРАБОТЧИКИ ======================

# 1. Команды (должны быть сверху!)
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id in OWNERS:
        bot.send_message(message.chat.id, "✅ Бот запущен.\nВы — владелец.")
    else:
        bot.send_message(message.chat.id, "👋 Привет, сосед! Здесь ты можешь анонимно отправить свой тейк о всем, что связано с Horrific Housing. Какие-то вопросы? Увидел что-то странное или смешное? Придумал мем? Присылай все это сюда!")


@bot.message_handler(commands=['myid'])
def myid(message):
    bot.send_message(
        message.chat.id,
        f"🆔 Ваш ID: <code>{message.chat.id}</code>\n\nОтправьте это число владельцам бота для добавления в владельцы.",
        parse_mode="HTML"
    )
    print(f"ID запрошен: {message.chat.id}")


# 2. Медиа (фото и видео)
@bot.message_handler(content_types=['photo', 'video'])
def handle_media(message):
    if message.chat.id in OWNERS:
        return

    if message.media_group_id:
        if message.media_group_id not in media_groups:
            media_groups[message.media_group_id] = {'messages': [], 'user_chat_id': message.chat.id, 'timer': None}

        group = media_groups[message.media_group_id]
        group['messages'].append(message)

        if group['timer']:
            group['timer'].cancel()
        group['timer'] = threading.Timer(2.0, process_album, args=[message.media_group_id])
        group['timer'].start()
    else:
        try:
            if message.photo:
                caption = (message.caption or "") + HASHTAG
                send_to_all_owners(photo=message.photo[-1].file_id, caption=caption)
            elif message.video:
                caption = (message.caption or "") + HASHTAG
                send_to_all_owners(video=message.video.file_id, caption=caption)
            bot.send_message(message.chat.id, "✅ Ваш тейк отправлен!")
        except:
            bot.send_message(message.chat.id, "✅ Ваш тейк отправлен!")


# 3. Обычный текст (самый последний!)
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.chat.id in OWNERS:
        return
    send_to_all_owners(text=message.text + HASHTAG)
    bot.send_message(message.chat.id, "✅ Ваш тейк отправлен!")


print("🤖 Бот запущен")
bot.infinity_polling()
