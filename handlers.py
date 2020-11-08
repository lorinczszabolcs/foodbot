import os
import random
from datetime import datetime
import json
from typing import List, Dict

import pandas as pd
from aito import api as aito_api
from aito.client import AitoClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from preference_voting import alloc_team_sample

import pandas as pd

AITO_INSTANCE_URL = "https://team1junction.aito.app"
AITO_API_KEY = os.environ.get("AITO_API_KEY")

client = AitoClient(AITO_INSTANCE_URL, AITO_API_KEY)


class PandasDB:
    def read(self, path="database_snapshot.csv") -> pd.DataFrame:
        return pd.read_csv("database_snapshot.csv")

    def write(self, dataframe: pd.DataFrame) -> None:
        dataframe.to_csv("database_snapshot.csv", index=False, header=True)


# ask preferences to the user
def askpreference(update: Update, df: pd.DataFrame, choice_number: int):

    # get data from dataset
    choices = df[df.user_id == update.effective_user.id].allocated_choices.values[0]
    choice = json.loads(choices)[choice_number]

    # buttons with options
    keyboard = [
        [
            InlineKeyboardButton(
                "FIRST CHOICE",
                callback_data=json.dumps(
                    {
                        "choice": choice_number,
                        "winner": choice[0].id,
                        "loser": choice[1].id,
                    }
                ),
            ),
            InlineKeyboardButton(
                "SECOND CHOICE",
                ccallback_data=json.dumps(
                    {
                        "choice": choice_number,
                        "winner": choice[1].id,
                        "loser": choice[0].id,
                    }
                ),
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # set of answers
    update.message.reply_text(text="Hey, take a look at the following options! :D:")
    update.message.reply_text(
        text="FIRST CHOICE: \n\n"
        + f"Name : {choice[0]['name']}\n"
        + f"Cuisine : {choice[0]['cuisine']}\n"
        + f"Address : {choice[0]['address']}\n"
        + f"Url : {choice[0]['url']}\n"
    )
    update.message.reply_text(
        text="SECOND CHOICE: \n\n"
        + f"Name : {choice[1]['name']}\n"
        + f"Cuisine : {choice[1]['cuisine']}\n"
        + f"Address : {choice[1]['address']}\n"
        + f"Url : {choice[1]['url']}\n",
    )
    update.message.reply_text(
        "Which of the following restaurants would you prefer?",
        reply_markup=reply_markup,
    )


def request_random_users(num_users: int) -> List[Dict]:
    query = {"from": "users", "select": ["userID"], "limit": 200}
    res = aito_api.generic_query(client, query)
    user_ids = res.json["hits"]
    return random.sample(user_ids, num_users)


def get_aito_recommendations(users: List[Dict[str, str]]) -> Dict:
    recommendation_query = {
        "from": "ratings",
        "where": {"userID": {"$or": [*users]}},
        "recommend": "placeID",
        "goal": {"rating": 2},
        "limit": 6,
    }
    res = aito_api.recommend(client, recommendation_query)
    places = res.json["hits"]
    for key, place in zip(range(len(places)), places):
        place["id"] = key
    return places


def voting_process_start(user_list: List[str]) -> None:
    # Matching of users to random users from DB
    random_users = request_random_users(len(user_list))

    # Getting recommendations based on users
    recommendations = get_aito_recommendations(random_users)

    # Allocations of rec choices
    rec_ids = [rec["id"] for rec in recommendations]
    allocations_ids = alloc_team_sample(rec_ids, len(random_users))

    # Write to DB
    hydrated_allocations = [
        [(recommendations[pair[0]], recommendations[pair[1]]) for pair in allocation]
        for allocation in allocations_ids
    ]

    for user, allocation_vec in zip(user_list, hydrated_allocations):
        db = PandasDB().read()
        db.loc[db.user_id == user, ["allocated_choices"]] = json.dumps(allocation_vec)
        PandasDB().write(db)


# Handlers
def start(update: Update, context: CallbackContext):

    df = PandasDB().read()
    grouptype = update.effective_chat.type

    if grouptype == "private":

        if update.effective_user.id in df.user_id.values.tolist():
            if df[df.user_id == update.effective_user.id]["registration_closed"].any():

                askpreference(update, df, 0)

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
                            "allocated_choices": " ",
                            "answers": "",
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
                            "allocated_choices": " ",
                            "answers": "[[],[]]",
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

        voting_process_start(db.user_id.unique().tolist())

        query.edit_message_text(
            "Thank you for joining, please look at your private chats with @foodvote_bot and send the /start command."
        )

    elif "choice" in query.data:

        previous_choice = json.loads(query.data)

        # save answers in the dataset
        answers = db[db.answers == update.effective_user.id]["answers"]
        answers = answers.values.tolist()

        if len(answer):
            pass
        else:
            answers = [[previous], []]

        # fmt: off
        import IPython ; IPython.embed()
        # fmt: on


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.",
    )
