import os


TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
WEBHOOK_TOKEN = os.environ.get('WEBHOOK_TOKEN')
DYNAMO_TABLE_HISTORY_CHAT = os.environ.get('DYNAMO_TABLE_HISTORY_CHAT', 'southon-bot-data-table-dev')
DYNAMO_TABLE_USER = os.environ.get('DYNAMO_TABLE_USER', 'southon-bot-user-table-dev')
DYNAMO_HOST = os.environ.get('DYNAMO_HOST', 'http://localhost:8000')