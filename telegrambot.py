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
    CallbackQueryHandler
)

from handlers import (
    start,
    unknown,
    button_answer,
    button
)

# tokens to interact with the bots
# 1405956615:AAGPs1Ta65Y1W8GBWlOKkzFeQejGsCviBXo new_test_bot
# 1440330193:AAHmGIYnqllLUBVl97DVflG48D_EPW0zZPI freefood_bot
# 1479496566:AAHOsvWBa6OQOrV0nuORHuJQkYTEIz8peik freeefoood_bot




if __name__ == "__main__":
    
    # access the bot
    updater = Updater(token='1405956615:AAGPs1Ta65Y1W8GBWlOKkzFeQejGsCviBXo', use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('button', button))
    dispatcher.add_handler(CallbackQueryHandler(button_answer))
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()