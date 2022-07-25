"""Small telegram bot."""

__author__ = 'Boris Polyanskiy'


import contextlib
from datetime import datetime
import logging
import os

import imaginator.entry as imaginator_entry
from telegram import ChatAction
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

MAX_TEXT_SIZE = 150

# load env variables
TOKEN = os.environ.get('TG_TOKEN')
if TOKEN is None:
    raise EnvironmentError('TG_TOKEN is not set')

# heroku settings
APP_NAME = os.environ.get('APP_NAME')
PORT = os.environ.get('PORT', '8443')

logging.info(f'load env: APP_NAME={APP_NAME}, PORT={PORT}')


def start(update, context):
    """Print welcome message and list of available commands."""
    text = (
        'I\'m an animation bot, please talk to me and I\'ll send you your '
        'animated text!'
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def echo(update, context):
    """Process incoming message and send animation."""
    logging.info(f"{update.effective_chat.username}: {update.message.text}")
    text = update.message.text.replace('\n', ' ')
    if len(text) > MAX_TEXT_SIZE:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Your message too long! Max message size is {MAX_TEXT_SIZE}',
        )
        return
    name = (
        f'{update.effective_chat.username}_{datetime.utcnow().timestamp()}.mp4'
    )
    try:
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id,
            action=ChatAction.UPLOAD_VIDEO,
        )
        imaginator = imaginator_entry.Imaginator()
        imaginator_entry.create_video(
            imaginator=imaginator,
            name=name,
            text_line=text,
        )
        with open(name, 'rb') as stream:
            context.bot.send_animation(
                chat_id=update.effective_chat.id,
                animation=stream,
                timeout=30
            )
    except Exception as err:
        logging.error(err)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text='Something wrong =(',
        )
    finally:
        with contextlib.suppress(OSError):
            os.remove(name)


updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# register handlers
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)


def main():
    """Start bot on heroku or locally (depending on env variables)."""
    if APP_NAME and PORT:
        # heroku host
        logging.info('Run on heroku')
        updater.start_webhook(listen='0.0.0.0', port=int(PORT), url_path=TOKEN)
        updater.bot.setWebhook(f'https://{APP_NAME}.herokuapp.com/{TOKEN}')
    else:
        # local host
        logging.info('Run on local host')
        updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
