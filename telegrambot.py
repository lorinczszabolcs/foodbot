import os
import logging

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)

from handlers import start, vote, results, button_handler, unknown

PORT = int(os.environ.get("PORT", 5000))
TG_TOKEN = os.environ.get("TG_TOKEN")


if __name__ == "__main__":

    # access the bot
    if not TG_TOKEN:
        raise Exception("No Telegram Bot token specified in the environment.")

    updater = Updater(token=TG_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("vote", vote))
    dispatcher.add_handler(CommandHandler("results", results))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TG_TOKEN)
    updater.bot.setWebhook("https://tgfoodvote.herokuapp.com/" + TG_TOKEN)
