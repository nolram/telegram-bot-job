import json
import logging


from telegram import Bot, Update
from telegram.ext import Dispatcher, handler

from .bot.chat import prepare_handler
from .utils import config

# Logging is cool!
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

def get_dispatcher(bot: Bot, update: Update) -> Dispatcher:
    """
    Configures the bot with a Telegram Token.
    Returns a bot instance.
    """

    dispatcher = Dispatcher(bot=bot, update_queue=None, workers=0)

    handlers = prepare_handler(update=update)
    for i in handlers:
        logger.info('Handler: {}'.format(i))
        dispatcher.add_handler(i)

    return dispatcher


def webhook(event, context):
    """
        Runs the Telegram webhook.
    """

    logger.info('Event: {}'.format(event))

    if event.get('body'):
        bot = get_bot()
        logger.info('Bot: {}'.format(bot))
        update = Update.de_json(json.loads(event.get('body')), bot)
        dispatcher = get_dispatcher(bot, update)
        logger.info('Dispatcher: {}'.format(dispatcher))
        logger.info('Update: {}'.format(update))
        dispatcher.process_update(update)

        return OK_RESPONSE
    return ERROR_RESPONSE


def set_webhook(event, context):
    """
    Sets the Telegram bot webhook.
    """

    logger.info('Event: {}'.format(event))
    bot = get_bot()
    url = 'https://{}/bot/{}'.format(
        event.get('headers').get('host'),
        config.WEBHOOK_TOKEN
    )
    webhook = bot.set_webhook(url)

    if webhook:
        return OK_RESPONSE

    return ERROR_RESPONSE