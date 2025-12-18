import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Patchelogia 🤍\n"
        "Здесь можно поделиться своим опытом с патчами или задать любой вопрос.\n"
        "Мы внимательно читаем каждое сообщение и обязательно вернёмся к тебе."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text if update.message.text else ""

    # автоответ пользователю
    await update.message.reply_text(
        "Спасибо 🤍\n"
        "Мы получили твоё сообщение и скоро вернёмся с ответом."
    )

    # пересылка админу
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"Сообщение от @{user.username or user.first_name}:\n{text}"
    )

    if update.message.photo or update.message.video:
        await update.message.forward(chat_id=ADMIN_CHAT_ID)

async def reply_from_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        original = update.message.reply_to_message
        if original.forward_from:
            user_id = original.forward_from.id
            await context.bot.send_message(
                chat_id=user_id,
                text=update.message.text
            )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.REPLY, reply_from_admin))

    app.run_polling()

if __name__ == "__main__":
    main()
