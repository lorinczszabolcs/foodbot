# FoodVote
## Making choosing a place to eat, fun and interactive ⚡⚡⚡
### Submission for Junction Connected 2020 - Aito.ai challenge.

[Link to working telegram bot.](https://t.me/foodvote_bot)

[Link to introduction video.](https://www.youtube.com/watch?v=e8WGjevAiwI) 

# Introduction
The main idea behind our project is to provide the recommendation power of [Aito.ai](https://aito.ai/) in a quick, interactive, clear and accessible format to teams who wish to have a fun and easy way of deciding about where to eat next time. Let us talk you through the main steps of how our idea would work in practice:


# How it works?
- The team makes a request to our telegram bot to organize a FoodVote, with a set of constraints and restaurant reviews;
- The bot then extracts a set of candidate restaurants based on a recommendation process that includes information about the individual team members, their constraints and restaurant reviews;
- FoodVote automatically ranks this set of candidate restaurants: it asks each team member to choose which restaurant they would prefer between two options from the candidate set, and based on all answers from all team members it calculates the ranking;
- The ranking is then displayed to the team, who have a ready made option to choose from, that is a direct result of a quick voting system of all team members. 
- At the end, users will be encouraged to provide feedback on the restaurant and to join in on the FoodVote fun all the while taking part inthe improvement of Aito recommendations.


# Technicalities
- Own dataset of restaurants constructed using [MyHelsinki OpenAPI](http://open-api.myhelsinki.fi/).
- Aito API provides set of recommended restaurants for a group of people, and is accessed through the [Aito Python SDK](https://aito-python-sdk.readthedocs.io/en/latest/).
- The set of recommended restaurants is then passed through a pairwise ranking system via the telegram bot. The ranking system is based on the Bradley-Terry algorithm, to be precise.
-  Our telegram bot is powered by a [Python interface](https://github.com/python-telegram-bot/python-telegram-bot) to the [Telegram Bot API](https://core.telegram.org/bots/api).


# Outlook 

- The same aproach can be used to integrate Aito with [slack](https://slack.com/intl/en-fi/), a popular chat application used in offices, and work teams, where such a service would be highly required.
