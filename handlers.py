from datetime import datetime
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
    MessageHandler,
    Filters,
    CallbackContext,
    CommandHandler,
    CallbackQueryHandler,
)

import pandas as pd
from enum import Enum


class PandasDB:
    def read(self, path="database.csv") -> pd.DataFrame:
        return pd.read_csv("database.csv")

    def write(self, dataframe: pd.DataFrame) -> None:
        dataframe.to_csv("database.csv", index=False, header=True)


# Handlers
def start(update: Update, context: CallbackContext):

    update.message.reply_text(
        text="Hey welcome to FoodVote! Type /vote to get started.",
    )


def vote(update: Update, context: CallbackContext):

    timestamp = datetime.now().isoformat()
    voting_id = update.effective_chat.id
    user_id = update.effective_user.id
    confirmed = False

    db = PandasDB().read()
    PandasDB().write(
        db.append(
            pd.DataFrame(
                {
                    "timestamp": timestamp,
                    "voting_id": voting_id,
                    "user_id": user_id,
                    "confirmed": confirmed,
                },
                index=[0],
            ),
            ignore_index=True,
        )
    )

    keyboard = [
        [
            InlineKeyboardButton("Join!", callback_data="join"),
            InlineKeyboardButton("Go to bot", url="https://t.me/foodvote_bot"),
        ],
        [
            InlineKeyboardButton("Close joining phase", callback_data="close"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "Voting session started, click the button below to join",
        reply_markup=reply_markup,
    )


def count_join(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "join":

        timestamp = datetime.now().isoformat()
        voting_id = update.effective_chat.id
        user_id = update.effective_user.id
        confirmed = False

        db = PandasDB().read()

        if (voting_id, user_id) not in zip(db.voting_id.tolist(), db.user_id.tolist()):
            PandasDB().write(
                db.append(
                    pd.DataFrame(
                        {
                            "timestamp": timestamp,
                            "voting_id": voting_id,
                            "user_id": user_id,
                            "confirmed": confirmed,
                        },
                        index=[0],
                    ),
                    ignore_index=True,
                )
            )
    elif query.data == "close":
        query.edit_message_text(
            "Thank you for joining, please look at your private chats with @foodvote_bot and send the start command."
        )


def echo(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def button(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton(
                "Option 1", url="tg://t.me/MattiaDoStuff_bot", callback_data="1"
            ),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        query.message.chat_id, "Please choose:", reply_markup=reply_markup
    )

    # update.message.reply_text("Please choose:", reply_markup=reply_markup)


def button_answer(update: Update, context: CallbackContext) -> None:

    pass
    # query = update.callback_query

    # # CallbackQueries need to be answered, even if no notification to the user is needed
    # # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    # query.answer()

    # keyboard = [
    #     [
    #         InlineKeyboardButton("Option 1", callback_data="1"),
    #         InlineKeyboardButton("Option 2", callback_data="2"),
    #     ]
    # ]

    # reply_markup = InlineKeyboardMarkup(keyboard)

    # context.bot.send_message(
    #     query.message.chat_id, "Please choose:", reply_markup=reply_markup
    # )


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.",
    )
