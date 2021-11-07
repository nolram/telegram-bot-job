import logging

from telegram import Bot

from telegram.ext import Updater

from bot.chat import prepare_handler

from models.dynamodb.user import HistoryChatModel

from utils import config

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def create_table() -> None:
    """
    Create the database table.
    """
    HistoryChatModel.create_table(read_capacity_units=1, write_capacity_units=1)

def delete_webhook() -> None:
    """
    Delete the Telegram bot webhook.
    """
    bot = Bot(token=config.TELEGRAM_TOKEN)
    url = ''
    bot.set_webhook(url)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    updater.bot.get_updates()

    # on different commands - answer in Telegram
    dispatcher.add_handler(prepare_handler(update=updater.bot.get_updates()))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    create_table()
    delete_webhook()
    main()