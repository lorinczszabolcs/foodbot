from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

import pandas as pd


class PandasDB:
    def read(self, path="database.csv") -> pd.DataFrame:
        return pd.read_csv("database.csv")

    def write(self, dataframe: pd.DataFrame) -> None:
        dataframe.to_csv("database.csv", index=False, header=True)


# Handlers
def start(update: Update, context: CallbackContext):

    df = PandasDB().read()
    grouptype = update.effective_chat.type

    if grouptype == "private":

        if update.effective_user.id in df.user_id.values.tolist():
            if df[df.user_id == update.effective_user.id]["registration_closed"].any():
                update.message.reply_text(
                    text="You are taking part of a voting! :D Here, these are your choices:",
                )
            else:
                update.message.reply_text(
                    text="The registrations for your voting is not closed yet! "
                    + "Go back and close it first in order to vote. No bugs allowed here! >:("
                )

        else:
            update.message.reply_text(
                text="Hey, welcome to FoodVote! Add me in a group and use the command /vote to start the voting! :)",
            )

    elif grouptype == "group" or grouptype == "supergroup":
        update.message.reply_text(
            text="Hey guys, welcome to FoodVote! Type /vote to get started.",
        )

    else:
        update.message.reply_text(
            text="Something bad happened here D:",
        )


def vote(update: Update, context: CallbackContext):

    grouptype = update.effective_chat.type
    if grouptype == "group" or grouptype == "supergroup":

        db = PandasDB().read()
        if update.effective_chat.id not in db.voting_id.tolist():

            timestamp = datetime.now().isoformat()
            voting_id = update.effective_chat.id
            user_id = update.effective_user.id
            registration_closed = False

            PandasDB().write(
                db.append(
                    pd.DataFrame(
                        {
                            "timestamp": timestamp,
                            "voting_id": voting_id,
                            "user_id": user_id,
                            "registration_closed": registration_closed,
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
                "Voting session started, click the button below to join the party!\n\nParticipants:"
                + "\n- @"
                + update.effective_user.username,
                reply_markup=reply_markup,
            )

        else:
            update.message.reply_text(
                "You already have a voting going on! No bugs allowed! >:("
            )

    else:
        update.message.reply_text(
            "I'm sorry, but this command is only available in groups"
        )


def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    db = PandasDB().read()

    if query.data == "join":

        timestamp = datetime.now().isoformat()
        voting_id = update.effective_chat.id
        user_id = update.effective_user.id
        registration_closed = False

        if (voting_id, user_id) not in zip(db.voting_id.tolist(), db.user_id.tolist()):
            PandasDB().write(
                db.append(
                    pd.DataFrame(
                        {
                            "timestamp": timestamp,
                            "voting_id": voting_id,
                            "user_id": user_id,
                            "registration_closed": registration_closed,
                        },
                        index=[0],
                    ),
                    ignore_index=True,
                )
            )

            query.edit_message_text(
                query.message.text + "\n- @" + update.effective_user.username,
                reply_markup=query.message.reply_markup,
            )

    elif query.data == "close":

        db.loc[db.voting_id == update.effective_chat.id, "registration_closed"] = True
        PandasDB().write(db)

        query.edit_message_text(
            "Thank you for joining, please look at your private chats with @foodvote_bot and send the start command."
        )


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.",
    )
