# Lessons status notifier

This bot is for notify Devman students about his lessons status.

## Requirements

 - python3.6+
 - `python-telegram-bot`
 - `environs`


## How to setup

This script uses Devman API and requires it's token. Just go [here](https://dvmn.org/api/docs/) and get the token.

Also you should [create telegram bot](https://core.telegram.org/bots#how-do-i-create-a-bot) and receive token

Use above information for fill settings in `.env` file. You can use `.env_example` as a template:
```
cp .env_example .env
vim .env
```

### How to run

Get the source code of this repo:
```
git clone git@github.com:leksuss/lesson_statuses_bot.git
```

Go inside folder:
```
cd lesson_statuses_bot
```

Python3 should be already installed. Then use pip (or pip3, if there is a conflict with Python2) to install dependencies:
```
# If you would like to install dependencies inside virtual environment, you should create it first.
pip3 install -r requirements.txt
```

Find your user's `chat_id`. To do this, just write to the bot [@userinfobot](https://t.me/userinfobot). This bot shows your ID, and for the user `chat_id` == `user_id`, so just find your ID. 

And then run bot:
```
python3 bot.py --chat_id <ID>  # <ID> - is your ID
```

## Goals
This project is made for study purpose.
