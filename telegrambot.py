import logging

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)

from handlers import start, vote, results, button_handler, unknown

# tokens to interact with the bots
# 1405956615:AAGPs1Ta65Y1W8GBWlOKkzFeQejGsCviBXo MattiaDoesStuff_bot
# 1440330193:AAHmGIYnqllLUBVl97DVflG48D_EPW0zZPI freefood_bot
# 1479496566:AAHOsvWBa6OQOrV0nuORHuJQkYTEIz8peik freeefoood_bot
# 1476500295:AAG83jTZTGzZz13M2zHfseIhXUg74cj_ApU foodvote_bot


if __name__ == "__main__":

    # access the bot
    updater = Updater(
        token="1476500295:AAG83jTZTGzZz13M2zHfseIhXUg74cj_ApU", use_context=True
    )
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

    updater.start_polling()
