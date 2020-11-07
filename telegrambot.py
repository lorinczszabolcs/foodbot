import time
import sys
import logging

from telegram import (
    Poll,
    ParseMode,
    KeyboardButton,
    KeyboardButtonPollType,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler,
    InlineQueryHandler,
)

from handlers import start, unknown, button_answer, button, vote, echo, count_join
import pandas as pd

# tokens to interact with the bots
# 1405956615:AAGPs1Ta65Y1W8GBWlOKkzFeQejGsCviBXo new_test_bot
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
    dispatcher.add_handler(CallbackQueryHandler(count_join))
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()
