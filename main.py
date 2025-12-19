import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# === Логирование ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Получаем переменные окружения ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not BOT_TOKEN or not ADMIN_CHAT_ID:
    raise EnvironmentError("BOT_TOKEN или ADMIN_CHAT_ID не заданы")

ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)

# === Карта forwarded message → user id ===
user_message_map = {}


# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет 🤍\n\n"
        "Сюда можно присылать скриншот из своей соцсети с Patchelogia.\n"
        "В ответ мы пришлём персональный промокод со скидкой 50% на следующий заказ.\n\n"
        "Если есть вопросы — просто напишите, мы будем рады помочь."
    )


# === Любое сообщение от пользователя ===
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = message.from_user

    # Ответ пользователю
    await message.reply_text("Спасибо 🤍\nМы получили сообщение и скоро вернёмся с ответом.")

    # Пересылка админу
    forwarded = await message.forward(chat_id=ADMIN_CHAT_ID)

    # Сохраняем соответствие
    user_message_map[forwarded.message_id] = user.id


# === Ответы админа в группе ===
async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message.reply_to_message:
        return

    forwarded_id = message.reply_to_message.message_id
    user_id = user_message_map.get(forwarded_id)

    if not user_id:
        logger.warning("Пользователь для этого ответа не найден.")
        return

    # Отправляем ответ пользователю
    if message.text:
        await context.bot.send_message(chat_id=user_id, text=message.text)
    elif message.photo:
        await context.bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=message.caption or "")
    elif message.video:
        await context.bot.send_video(chat_id=user_id, video=message.video.file_id, caption=message.caption or "")
    elif message.document:
        await context.bot.send_document(chat_id=user_id, document=message.document.file_id, caption=message.caption or "")
    elif message.sticker:
        await context.bot.send_sticker(chat_id=user_id, sticker=message.sticker.file_id)
    else:
        await context.bot.send_message(chat_id=user_id, text="(не удалось переслать это сообщение пользователю)")


# === Точка входа ===
def main():
    logger.info("Запуск Telegram-бота...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.Chat(ADMIN_CHAT_ID), handle_user_message))
    app.add_handler(MessageHandler(filters.Chat(ADMIN_CHAT_ID) & filters.REPLY, handle_admin_reply))

    logger.info("Бот запущен и слушает обновления...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
