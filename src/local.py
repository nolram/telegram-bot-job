import logging

from .utils import config

from telegram import Bot

from telegram.ext import Updater

from .bot.commands import prepare_handler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def delete_webhook() -> None:
    """
    Delete the Telegram bot webhook.
    """
    bot = Bot(token=config.TELEGRAM_TOKEN)
    url = ''
    webhook = bot.set_webhook(url)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(prepare_handler())
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    # delete_webhook()
    main()