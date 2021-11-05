import json
import logging


from telegram import Bot, Update
from telegram.ext import Dispatcher

from .bot.commands import prepare_handler
from .utils import config

# Logging is cool!
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(level=logging.INFO)

OK_RESPONSE = {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps('ok')
}
ERROR_RESPONSE = {
    'statusCode': 400,
    'body': json.dumps('Oops, something went wrong!')
}

def get_bot() -> Bot:
    """
        Configures the bot with a Telegram Token.
        Returns a bot instance.
    """

    TELEGRAM_TOKEN = config.TELEGRAM_TOKEN
    if not TELEGRAM_TOKEN:
        logger.error('The TELEGRAM_TOKEN must be set')
        raise NotImplementedError
    return Bot(token=TELEGRAM_TOKEN)

def get_dispatcher(bot: Bot) -> Dispatcher:
    """
    Configures the bot with a Telegram Token.
    Returns a bot instance.
    """

    dispatcher = Dispatcher(bot, None, workers=0)
    dispatcher.add_handler(prepare_handler())

    return dispatcher


def webhook(event, context):
    """
        Runs the Telegram webhook.
    """

    bot = get_bot()
    dispatcher = get_dispatcher(bot)

    logger.info('Event: {}'.format(event))

    if event.get('body'):
        update = Update.de_json(json.loads(event.get('body')), bot)
        dispatcher.process_update(update)
        return OK_RESPONSE
    return ERROR_RESPONSE


def set_webhook(event, context):
    """
    Sets the Telegram bot webhook.
    """

    logger.info('Event: {}'.format(event))
    bot = get_bot()
    url = 'https://{}/{}'.format(
        event.get('headers').get('host'),
        config.WEBHOOK_TOKEN
    )
    webhook = bot.set_webhook(url)

    if webhook:
        return OK_RESPONSE

    return ERROR_RESPONSE