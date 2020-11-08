import os
import random
from datetime import datetime
import numpy as np
import json
from typing import List, Dict

import pandas as pd
from aito import api as aito_api
from aito.client import AitoClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from preference_voting import alloc_team_sample, voteaggregate, btm


AITO_INSTANCE_URL = "https://team1junction.aito.app"
AITO_API_KEY = os.environ.get("AITO_API_KEY")

client = AitoClient(AITO_INSTANCE_URL, AITO_API_KEY)


class PandasDB:
    def read(self, path="database.csv") -> pd.DataFrame:
        return pd.read_csv("database.csv")

    def write(self, dataframe: pd.DataFrame) -> None:
        dataframe.to_csv("database.csv", index=False, header=True)


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
        [[recommendations[pair[0]], recommendations[pair[1]]] for pair in allocation]
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

                # get data from dataset
                choices = json.loads(
                    df[df.user_id == update.effective_user.id].allocated_choices.values[
                        0
                    ]
                )
                choice = choices[0]

                # buttons with options
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "FIRST CHOICE",
                            callback_data=json.dumps(
                                {
                                    "choice": 0,
                                    "winner": choice[0]["id"],
                                    "loser": choice[1]["id"],
                                }
                            ),
                        ),
                        InlineKeyboardButton(
                            "SECOND CHOICE",
                            callback_data=json.dumps(
                                {
                                    "choice": 0,
                                    "winner": choice[1]["id"],
                                    "loser": choice[0]["id"],
                                }
                            ),
                        ),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                # set of answers
                update.message.reply_text(
                    text=f"Hey, take a look at the following options! 1/{len(choices)}"
                )
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
                            "finished_answers": False,
                            "tg_username": update.effective_user.username,
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


def results(update: Update, context: CallbackContext):
    grouptype = update.effective_chat.type

    if grouptype == "private":
        update.message.reply_text(
            "Not so fast! This command is only available in groups."
        )
    else:
        db = PandasDB().read()
        check_complete = db[db["voting_id"] == update.effective_chat.id][
            "finished_answers"
        ].all()

        if check_complete:
            # Must do algorithm
            vectors = db[db["voting_id"] == update.effective_chat.id][
                "answers"
            ].tolist()

            winners = []
            losers = []
            for mat in [json.loads(vec) for vec in vectors]:
                winners += mat[0]
                losers += mat[1]

            restaurant_name = np.unique(winners + losers).tolist()
            votes_matrix = voteaggregate(winners, losers, restaurant_name)
            pref_matrix = btm(votes_matrix, restaurant_name)

            index_best = pref_matrix[0][pref_matrix[1].index(np.max(pref_matrix[1]))]

            all_choices: List[Dict] = sum(
                [json.loads(vec) for vec in db["allocated_choices"].tolist()], []
            )

            best_choice: Dict = {}
            found = False
            i = 0
            while not found and i < len(all_choices):
                for current_choice in all_choices[i]:
                    if current_choice["id"] == index_best:
                        best_choice = current_choice
                        found = True
                    else:
                        i += 1

            update.message.reply_text(
                text="This is the outcome of the vote (counting all the choices, not like Nevada): \n\n"
                + f"Name : {best_choice['name']}\n"
                + f"Cuisine : {best_choice['cuisine']}\n"
                + f"Address : {best_choice['address']}\n"
                + f"Url : {best_choice['url']}\n"
            )
            update.message.reply_text(
                text="Thank you for using FoodVote! Hope to see you soon :)"
            )
            db = db[db["voting_id"] != update.effective_chat.id]
            PandasDB().write(db)

        else:
            who_is_late = db[
                ~(db[db["voting_id"] == update.effective_chat.id]["finished_answers"])
            ]["tg_username"].tolist()
            update.message.reply_text(
                "Can't calculate the results yet! >:(\n\nThese people are still missing:\n"
                + "".join([f"@{name}\n" for name in who_is_late])
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
                            "answers": "",
                            "finished_answers": False,
                            "tg_username": update.effective_user.username,
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

        future_choice = previous_choice["choice"]
        choices_number = len(
            json.loads(
                db[db.user_id == update.effective_user.id]["allocated_choices"].iloc[0]
            )
        )
        if future_choice < choices_number - 1:
            # save answers in the dataset
            answers = db[db.user_id == update.effective_user.id]["answers"].dropna()
            answers = answers.values.tolist()

            if len(answers) > 0:
                answers = json.loads(answers[0])
                answers[0] += [previous_choice["winner"]]
                answers[1] += [previous_choice["loser"]]
            else:
                answers = [[previous_choice["winner"]], [previous_choice["loser"]]]

            db.loc[db.user_id == update.effective_user.id, ["answers"]] = json.dumps(
                answers
            )
            PandasDB().write(db)

            future_choice += 1

            # get data from dataset
            choices = db[
                db.user_id == update.effective_user.id
            ].allocated_choices.values[0]
            choice = json.loads(choices)[future_choice]

            # buttons with options
            keyboard = [
                [
                    InlineKeyboardButton(
                        "FIRST CHOICE",
                        callback_data=json.dumps(
                            {
                                "choice": future_choice,
                                "winner": choice[0]["id"],
                                "loser": choice[1]["id"],
                            }
                        ),
                    ),
                    InlineKeyboardButton(
                        "SECOND CHOICE",
                        callback_data=json.dumps(
                            {
                                "choice": future_choice,
                                "winner": choice[1]["id"],
                                "loser": choice[0]["id"],
                            }
                        ),
                    ),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # set of answers
            context.bot.sendMessage(
                query.message.chat_id,
                text=f"Hey, take a look at the following options! {future_choice+1}/{choices_number}",
            )
            context.bot.sendMessage(
                query.message.chat_id,
                text="FIRST CHOICE: \n\n"
                + f"Name : {choice[0]['name']}\n"
                + f"Cuisine : {choice[0]['cuisine']}\n"
                + f"Address : {choice[0]['address']}\n"
                + f"Url : {choice[0]['url']}\n",
            )
            context.bot.sendMessage(
                query.message.chat_id,
                text="SECOND CHOICE: \n\n"
                + f"Name : {choice[1]['name']}\n"
                + f"Cuisine : {choice[1]['cuisine']}\n"
                + f"Address : {choice[1]['address']}\n"
                + f"Url : {choice[1]['url']}\n",
            )
            context.bot.sendMessage(
                query.message.chat_id,
                "Which of the following restaurants would you prefer?",
                reply_markup=reply_markup,
            )
        else:
            db.loc[db.user_id == update.effective_user.id, ["finished_answers"]] = True
            PandasDB().write(db)

            context.bot.sendMessage(
                query.message.chat_id,
                "Thanks for you responses, head back to your group and use the command /results to see your destination :D",
            )


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.",
    )
