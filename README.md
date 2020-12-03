# mbc-tg-bot
Small telegram bot for sending animations.

User writes message to bot, bot return message text as animation.

## Requirements
* python 3.6+
* packages from requirements.txt file:
  ```
  pip install -r requirements.txt
  ```
* `libgl1` (on debian)

## Environment variables
Script reads next parameters from environment variables:
* `TG_TOKEN` - telegram token of your bot

## Run on heroku
For run bot on heroku you also need to set next variables:
* `APP_NAME` - name of your heroku application: https://<APP_NAME>.herokuapp.com
