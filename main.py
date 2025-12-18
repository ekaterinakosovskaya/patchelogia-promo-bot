import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Patchelogia 🤍\n"
        "Здесь можно поделиться своим опытом с патчами или задать любой вопрос.\n"
        "Мы внимательно читаем каждое сообщение и обязательно вернёмся с ответом."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # автоответ пользователю
    await update.message.reply_text(
        "Спасибо 🤍\n"
        "Мы получили сообщение и скоро вернёмся с ответом."
    )

    # пересылка сообщения в админ-чат
    await context.bot.forward_message(
        chat_id=ADMIN_CHAT_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

async def reply_from_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and update.message.reply_to_message.forward_from:
        user_id = update.message.reply_to_message.forward_from.id
        await context.bot.send_message(
            chat_id=user_id,
            text=update.message.text
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.REPLY & filters.Chat(ADMIN_CHAT_ID), reply_from_admin))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
